import actual_hydro
from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
#from fastai.vision import *
from flask import Response
from subprocess import check_output, STDOUT
import uuid
import pymongo
import os
from os import path
import shutil
import pymongo
import dns
from pymongo import MongoClient
from bson.objectid import ObjectId





app = Flask(__name__)
api = Api(app)

    
class PlantGrowth(Resource):
    def __init__(self):
        #print('flask')
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument( "ImagePath", type=str, required=True, help="Please provide the path to the image")
        self.reqparser.add_argument( "system", type=str, required=True, help="Please provide the system")
        self.reqparser.add_argument( "PlantId", type=str, required=True, help="Please provide the Plant Id")
        self.reqparser.add_argument( "apitype", type=str, required=True, help="Please provide the API Type")
        self.reqparser.add_argument( "CustomerDb", type=str, required=True, help="Please provide the name to the customer database")
    
        self.gsutil = "gsutil -m cp gs://hydrotekai/"  
   
    def get(self):
        
        args = self.reqparser.parse_args()
        
        self.imagepath = args['ImagePath']
        self.bucketname_m = args['system']
        self.plantid = args['PlantId']
        self.customerdb = args['CustomerDb']
        self.apitype = args['apitype']
     
        
        #intput_dir = "systemfile"
        #intput_dir_image = "inputfiles"
        intput_dir_image = "inputfiles"+str(uuid.uuid1())

        
        jsonfile = {}
        measure = {}
         
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
            col = client[self.customerdb].PlantGrowth  
            print("Connected to MongoDB.")
            
            
            jsonfile['_id'] = str(ObjectId())
            jsonfile['status'] = "SUCCESS"
            
            #creating directory for input file
            #os.mkdir(intput_dir)
            
            #creating directory for input file
            os.mkdir(intput_dir_image)
            
            #paths to input files
            imagepath_on_system = intput_dir_image + "/" + args['ImagePath'].split('/')[-1]
            imagepath_on_system = args['ImagePath']
            #model_path_on_system = intput_dir + "/" 
            
            #downloading input files
            #cmd_dwnld_models = self.gsutil + self.bucketname_m + " " + intput_dir
            #cmd_stdout_models = check_output(cmd_dwnld_models, stderr=STDOUT, shell=True)
                        
            cmd_dwnld_image = self.gsutil + self.imagepath + " " + imagepath_on_system
            cmd_stdout_image = check_output(cmd_dwnld_image, stderr=STDOUT, shell=True)
                        
            
            
            measure['height'],measure['width'],measure['timestamp'] = actual_hydro.test(imagepath_on_system,self.bucketname_m)
            print(measure)
            #jsonfile['height'],jsonfile['width'],jsonfile['timestamp'] = actual_hydro.test(imagepath_on_system,self.bucketname_m)
            #jsonfile['Height'] = actual_hydro.test(imagepath_on_system,self.bucketname_m)
            
            existing_plantId = col.find({"plantId":self.plantid})

            if existing_plantId.count() > 0:
                jsonfile = col.find_one_and_update({'plantId':self.plantid},
                                                          {'$push': {'measurements':{'height': measure['height'],'width': measure['width'],'timestamp': measure['timestamp']}}})
            else: 
                jsonfile = col.insert_one({'plantId':self.plantid,
                                           'measurements':[{'height': measure['height'],'width': measure['width'],'timestamp': measure['timestamp']}],
                                           'status':'SUCCESS'})
            
        except Exception as ex:
            jsonfile = col.insert_one({'plantId':self.plantid,'errorDescription':str(ex),'status':'FAIL'})
            return jsonfile


api.add_resource(PlantGrowth, "/PlantGrowth")

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=6003, debug='TRUE')
