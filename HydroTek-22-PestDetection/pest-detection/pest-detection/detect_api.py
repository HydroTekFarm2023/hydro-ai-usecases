import torch
import cv2
from PIL import Image
from flask import Flask, request
from flask_restful import reqparse
from subprocess import check_output, STDOUT
from pymongo import MongoClient
from pprint import pprint
import datetime
import os


classes = []
with open("classes.txt", "r") as f:
    data = f.read()
    lines = data.split("\n")
    for line in lines:
        split = line.split(" ")
        class_ = " ".join(split[1:])
        classes.append(class_.strip())


model = torch.hub.load('./yolov5/yolov5', 'custom', path='pest-37.pt', source='local')  
def detect(model, imgName):
    img = Image.open(imgName)
    imgs = [img]  
    model.conf = 0.2
    results = model(imgs, size=416)
    print(results.pandas().xyxy[0])
    xmin = list(results.pandas().xyxy[0]['xmin'])
    xmax = list(results.pandas().xyxy[0]['xmax'])
    ymin = list(results.pandas().xyxy[0]['ymin'])
    ymax = list(results.pandas().xyxy[0]['ymax'])
    c = list(results.pandas().xyxy[0]['class'])
    conf = list(results.pandas().xyxy[0]['confidence'])
    

    for i in range(0,len(xmin)):
        cv2.rectangle(imgs[0], (int(xmin[i]), int(ymin[i])), (int(xmax[i]), int(ymax[i])), (0, 0, 220), 8)
        #cv2.putText(imgs[0], c[i]+" "+str(int(conf[i]*100))+"%", (int(xmin[i]), int(ymin[i])-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 220), 2)
        cv2.putText(imgs[0], classes[int(c[i])]+" "+str(int(conf[i]*100))+"%", (int(xmin[i]), int(ymin[i])-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 220), 1)
        print(classes[int(c[i])], str(int(conf[i]*100))+"%")
    print(results.imgs[0].shape)        
    x = imgs[0].shape[0]
    y = imgs[0].shape[1]
    out = cv2.resize(results.imgs[0],(y,x),interpolation = cv2.INTER_AREA)[..., ::-1]
    cv2.imwrite(imgName.split(".")[0]+"-output.jpg",out)
    results = results.pandas().xyxy[0].to_dict('list')
    results['pest'] = []
    for i in range(0, len(xmin)):
        results['pest'].append(classes[int(c[i])])
    return results


app_flask = Flask(__name__)
parser = reqparse.RequestParser()
parser.add_argument('source', type=str, required=True, help="Enter source directory")
parser.add_argument('imageName', type=str, required=True, help="Enter Image Name")
parser.add_argument('dest', type=str, required=True, help="Enter destination directory")
#parser.add_argument('weights', type=str,required=True, help="Enter weights location")

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
        "pestPresent": False,
        "timestamp" : time,
        "status": "SUCCESS"
                        }
    if(len(result['xmin']) > 0):
        insert_json["pestPresent"] = True
        insert_json["result"] = result["pest"][0]
    record["healthMonitor"].append(insert_json)
    ret = db.results.update_one({ 'stationId': id }, { "$set": { 'healthMonitor': record["healthMonitor"] } }) 
    return (ret)

def get_value_from_key(results,name):
    for result in results:
        if(name == result["pest"]):
            return result["treatment"]
    return "None"

def get_treatment(db, pests):
    names = pests["pest"]
    treatments = db.treatment.find()
    pests["treatment"] = []
    for name in names:
        pests["treatment"].append(get_value_from_key(treatments, name))
    return pests

db = connect()


@app_flask.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    #response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    
    return response



@app_flask.route('/v1/pestdetection/', methods=['GET'])
def home():
    if request.method == 'GET' or request.method == 'POST':
        return "Pest Detection Server is running v2!!"


@app_flask.route('/v1/pestdetection/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'GET' or request.method == 'POST':
        args = request.args
        source = args['source']
        dest = args['dest']
        imageName = args['imageName']
        dwnImg = "gsutil cp gs://"+source+"/"+imageName + " " + "./"
        check_output(dwnImg, stderr=STDOUT, shell=True)
        results = detect(model,imageName)
        print(results)
        db_insert(db,1,imageName,results)
        uploadImg = "gsutil cp "+imageName.split(".")[0]+"-output.jpg"+" gs://"+dest
        print(uploadImg)
        check_output(uploadImg, stderr=STDOUT, shell=True)
        return results

@app_flask.route('/v1/pestdetection/treatment', methods=['GET', 'POST'])
def treatment():
    if request.method == 'GET' or request.method == 'POST':
        args = request.args
        source = args['source']
        dest = args['dest']
        imageName = args['imageName']
        dwnImg = "gsutil cp gs://"+source+"/"+imageName + " " + "./"
        check_output(dwnImg, stderr=STDOUT, shell=True)
        results = detect(model,imageName)
        #print(results)
        db_insert(db,1,imageName,results)
        results = get_treatment(db, results)
        results["image"] = dest+"/"+imageName.split(".")[0]+"-output.jpg"
        uploadImg = "gsutil cp "+imageName.split(".")[0]+"-output.jpg"+" gs://"+dest
        #print(uploadImg)
        check_output(uploadImg, stderr=STDOUT, shell=True)
        return results

if __name__ == '__main__':
    app_flask.run(host='0.0.0.0',port=5001,debug=True)