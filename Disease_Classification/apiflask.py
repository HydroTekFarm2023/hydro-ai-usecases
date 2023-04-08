import disease_classification
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

import pymongo
import dns
from pymongo import MongoClient
from bson import ObjectId





app = Flask(__name__)
api = Api(app)

    
class getDiseaseClass(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument( "ImagePath", type=str, required=True, help="Please provide the path to the image")
        self.reqparser.add_argument( "ModelPath", type=str, required=True, help="Please provide the path to the image")
        self.reqparser.add_argument( "PlantId", type=str, required=True, help="Please provide the path to the image")
    
        self.gsutil = "gsutil -m cp gs://hydrotekai/"  
   
    def get(self):
        
        args = self.reqparser.parse_args()
        
        self.imagepath = args['ImagePath']
        self.bucketname_m = args['ModelPath']
        self.plantid = args['PlantId']
     
        
        input_dir = "inputfiles"+str(uuid.uuid1())
        
        jsonfile = {}
         
        try:
            
            
            client = pymongo.MongoClient("mongodb+srv://hydrotekai:Kansas2020!m@cluster0.x5wba.gcp.mongodb.net/hydrotekaidb?retryWrites=true&w=majority")
            db = client.get_database('hydrotekaidb')
            col = db.DiseaseClassification
           
            
            
            #creating directory for input file
            os.mkdir(input_dir)
            
    
            
            #paths to input files
            imagepath_on_system = input_dir + "/" + args['ImagePath'].split('/')[-1]
            model_path_on_system = input_dir + "/" +args['ModelPath'].split('/')[-1]
            
            #downloading input files
    
            cmd_dwnld_models = self.gsutil + self.bucketname_m + " " + model_path_on_system
            cmd_stdout_models = check_output(cmd_dwnld_models, stderr=STDOUT, shell=True)
            print("Downloaded the model")
                        
            cmd_dwnld_image = self.gsutil + self.imagepath + " " + imagepath_on_system
            cmd_stdout_image = check_output(cmd_dwnld_image, stderr=STDOUT, shell=True)
            print("Downloaded the image")
            
            diseaseType = disease_classification.test(imagepath_on_system,model_path_on_system)
            
            existing_plantId = col.find({"plantId":self.plantid})
            if existing_plantId.count() > 0:
                jsonfile = col.find_one_and_update({'plantId':self.plantid},
                                                          {'$push': {'healthMonitor':{'diseaseType': diseaseType}}})
            else: 
                jsonfile = col.insert_one({'plantId':self.plantid,'healthMonitor':[{'diseaseType': diseaseType}],'status':'SUCCESS'})
            
        except Exception as ex:
            jsonfile = col.insert_one({'plantId':self.plantid,'errorDescription':str(ex),'status':'FAIL'})
            return jsonfile

api.add_resource(getDiseaseClass, "/diseaseclassification")

if __name__ == '__main__':
    app.run('0.0.0.0',6001,threaded=False)