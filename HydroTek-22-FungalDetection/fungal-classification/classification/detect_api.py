from flask import Flask, request
from flask_restful import reqparse
from subprocess import check_output, STDOUT
from pymongo import MongoClient
from fastbook import *
from fastai.vision.widgets import *
import os
import datetime
from fastai.vision import *


learner = load_learner('./export.pkl')
def detect(learner, image_name,image_path,model_name,model_path):
    learner = load_model(learner,model_name,model_path)
    load_image(image_name,image_path)
    results = learner.predict('./' + image_name)
    return results

def load_model(learner,model_name,model_path):
    gs_model_load_query = 'gsutil cp -r gs://' + model_path + '/' + model_name + ".pkl ./"
    print(gs_model_load_query)
    check_output(gs_model_load_query, stderr=STDOUT, shell=True)
    print(model_name)
    learner = load_learner('./' + model_name + '.pkl')
    return learner

def load_image(image_name,image_path):
    gs_image_load_query = 'gsutil cp -r gs://' + image_path + '/' + image_name +' ./'
    print(gs_image_load_query)
    check_output(gs_image_load_query, stderr=STDOUT, shell=True)

app_flask = Flask(__name__)
parser = reqparse.RequestParser()
parser.add_argument('image_name', type=str, required=True, help="Enter source directory")
parser.add_argument('image_path', type=str, required=True, help="Enter Image Name")
parser.add_argument('model_name', type=str, required=True, help="Enter destination directory")
parser.add_argument('model_path', type=str,required=True, help="Enter weights location")

def connect():
    username = os.getenv("MONGO_USER", default="hydrotekai")
    pwd = os.getenv("MONGO_PWD", default="Kansas2020!m")
    host = os.getenv("MONGO_HOST", default="cluster0.x5wba.gcp.mongodb.net")

    mongocmd = ("mongodb+srv://{}:{}@" + host + "/" + 'hydrotek' + "?retryWrites=false")
    client = MongoClient(mongocmd.format(username, pwd))
    db = client.hydrotek
    return db


def db_insert(db,id,image,result,time=datetime.datetime.now()):
    record = db.results.find_one({"stationId": id})
    #print(record)
    insert_json = {
        "imageId" : image,
        "disease": False,
        "timestamp" : time,
        "status": "SUCCESS"
                        }
    if("healthy" not in result[0]):
        insert_json["disease"] = True
        insert_json["result"] = result[0]
    record["healthMonitor"].append(insert_json)
    ret = db.results.update_one({ 'stationId': id }, { "$set": { 'healthMonitor': record["healthMonitor"] } }) 
    return (ret)

def get_value_from_key(results,name):
    for result in results:
        if(name == result["disease"]):
            return result["treatment"]
    return "None"

def get_treatment(db, result):
    names = result[0]
    treatments = db["fungal-treatment"].find()
    print(treatments)
    results = {}
    results["treatment"] = []
    results["treatment"].append(get_value_from_key(treatments, names))
    return results["treatment"]

db = connect()

@app_flask.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    #response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    
    return response


@app_flask.route('/v1/fungaldetection/', methods=['GET'])
def home():
    if request.method == 'GET' or request.method == 'POST':
        return "Fungal Detection Server is running!"


@app_flask.route('/v1/fungalclassification/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'GET' or request.method == 'POST':
        args = request.args
        image_name = args['imageName']
        image_path = args['source']
        model_name = args['model_name']
        model_path = args['model_path']
        dest = args['dest']
        results = detect(learner,image_name,image_path,model_name,model_path)
        print(results)
        db_insert(db,1,image_name,results)
        uploadImg = "gsutil cp "+image_name+" gs://"+dest+"/"+image_name.split(".")[0]+"-output.jpg"
        print(uploadImg)
        check_output(uploadImg, stderr=STDOUT, shell=True)
        return {'class' : results[0],'confidence' : float(results[2][int(results[1])])}

@app_flask.route('/v1/fungalclassification/treatment', methods=['GET', 'POST'])
def treatment():
    if request.method == 'GET' or request.method == 'POST':
        args = request.args
        image_name = args['imageName']
        image_path = args['source']
        model_name = args['model_name']
        model_path = args['model_path']
        dest = args['dest']
        results = detect(learner,image_name,image_path,model_name,model_path)
        #print(results)
        if("healthy" in results[0]):
            return {'class' : results[0],'confidence' : float(results[2][int(results[1])])}
        db_insert(db,1,image_name,results)
        treatment = get_treatment(db, results)
        uploadImg = "gsutil cp "+image_name+" gs://"+dest+"/"+image_name.split(".")[0]+"-output.jpg"
        print(uploadImg)
        check_output(uploadImg, stderr=STDOUT, shell=True)
        image = dest+"/"+image_name.split(".")[0]+"-output.jpg"
        return {'class' : results[0],'confidence' : float(results[2][int(results[1])]), "treatment":treatment, "image": image }

if __name__ == '__main__':
    app_flask.run(host='0.0.0.0',port=5001,debug=True)