import model_train
from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
from fastai.vision import *
from flask import Response
from subprocess import check_output, STDOUT
import pymongo
import os
from os import path
import shutil
import uuid
import tarfile
import pymongo
import dns
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import time




app = Flask(__name__)
api = Api(app)
uuid=str(uuid.uuid1())
print(uuid)
path = os.getcwd()
    
class trainDisease(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument( "ImagePath", type=str, required=True, help="Please provide the path to the image")
        self.reqparser.add_argument( "PlantType", type=str, required=True, help="Please provide the path to the image")
        self.reqparser.add_argument( "apitype", type=str, required=True, help="Please provide the API Type")
        self.reqparser.add_argument( "CustomerDb", type=str, required=True, help="Please provide the name to the customer database")
        self.gsutil = "gsutil -m cp gs://hydrotekai/"  
   
    def get(self):
        
        args = self.reqparser.parse_args()
        self.imagepath = args['ImagePath']
        self.plantname = args['PlantType']
        self.customerdb = args['CustomerDb']
        self.apitype = args['apitype']
     
        datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        input_dir = "inputfiles"+uuid
        #extract_dir = "extractfiles"+str(uuid.uuid1())
        jsonfile = {}
         
        try:
            print("Connecting to MongoDB.")
            username = os.getenv("MONGO_USER", default="hydrotekai")
            pwd = os.getenv("MONGO_PWD", default="Kansas2020!m")
            host = os.getenv("MONGO_HOST", default="cluster0.x5wba.gcp.mongodb.net")
            port = os.getenv("MONGO_PORT", default="27017")
            # mongocmd = ""
            if self.apitype == "dev" or self.apitype == "devtest":
                mongocmd = ("mongodb+srv://{}:{}@" + host + "/" + self.customerdb + "?retryWrites=false")
            else:
                mongocmd = ("mongodb://{}:{}@" + host + ":" + port + "/" + self.customerdb + "?retryWrites=false")
            client = MongoClient(mongocmd.format(username, pwd))
            col = client[self.customerdb].TrainedModelDetail   
            print("Connected to MongoDB.")


            #creating directory for input file
            os.mkdir(input_dir)
            #os.mkdir(extract_dir)
            
    
            
            #paths to input files
            imagepath_on_system =input_dir + "/" + args['ImagePath'].split('/')[-1]
            extracted_file = input_dir+"/"+"extract"+"/"
            
            
            #downloading input files

            cmd_dwnld_image = self.gsutil + self.imagepath + " " + imagepath_on_system
            cmd_stdout_image = check_output(cmd_dwnld_image, stderr=STDOUT, shell=True)
            print("Downloaded the images")
            
            image_extract= tarfile.open(imagepath_on_system)
            image_extract.extractall(extracted_file)
            print("extracted the images")
            model_training_path = input_dir+"/"+"extract"+"/"+self.plantname+"/"
            print("Path for image training created")
        
            data = model_train.test(model_training_path)
            
            score = data.to_dict("records")
            print(score)
            
            print("Model Trained and Saved at Local")
            os.system("cp"+" "+model_training_path+"export.pkl"+" "+model_training_path+"export"+uuid+".pkl")
            upload_model = "gsutil cp -r"+" " +model_training_path+"export"+uuid+".pkl"+" "+"gs://hydrotekai/DiseaseClassificationModel/"+self.plantname+"/"
            cmd_stdout_model = check_output(upload_model, stderr=STDOUT, shell=True)
            print("Trained Model Uploaded to GCP")
            path_to_gcp = "gs://hydrotekai/DiseaseClassificationModel/"+self.plantname+"/"+"export"+uuid+".pkl"
            print("Updating the database")
            existing_plantname = col.find({"plantType":self.plantname})
            if existing_plantname.count() > 0:
                jsonfile = col.find_one_and_update({"plantType":self.plantname},
                                                          {'$push': {'ModelMonitor':{'modelpath': path_to_gcp,
                                                                                     'train_score':score,
                                                                                     'Timestamp':datetime_now,
                                                                                     'status':'SUCCESS'}}})
            else: 
                jsonfile = col.insert_one({'plantType':self.plantname,
                                           'ModelMonitor':[{'modelpath': path_to_gcp,
                                                            'train_score':score,
                                           'Timestamp':datetime_now}],
                                           'status':'SUCCESS'})
            print("Database Updated")
        except Exception as ex:
            jsonfile = col.insert_one({"plantType":self.plantname,'errorDescription':str(ex),
                                       'Timestamp':datetime_now,'status':'FAIL'})
            print("Database Updated")
            return jsonfile

api.add_resource(trainDisease, "/modeltraining")


if __name__ == '__main__':
    app.run('0.0.0.0',6005,threaded=True)

