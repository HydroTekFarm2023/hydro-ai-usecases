import actual_hydro
from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
#from fastai.vision import *
from flask import Response
from subprocess import check_output, STDOUT
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
    
        self.gsutil = "gsutil -m cp gs://hydrotekai/"  
   
    def get(self):
        
        args = self.reqparser.parse_args()
        
        self.imagepath = args['ImagePath']
        self.bucketname_m = args['system']
     
        
        #intput_dir = "systemfile"
        intput_dir_image = "inputfiles"
        
        jsonfile = {}
         
        try:
            

            client = pymongo.MongoClient("mongodb+srv://hydrotekai:Kansas2020!m@cluster0.x5wba.gcp.mongodb.net/hydrotekaidb?retryWrites=true&w=majority")
            db = client.get_database('hydrotekaidb')
            collection = db.PlantGrowth
            
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
                        
            
            
            jsonfile['Height'],jsonfile['Weight'],jsonfile['Timestamp'] = actual_hydro.test(imagepath_on_system,self.bucketname_m)
            #jsonfile['Height'] = actual_hydro.test(imagepath_on_system,self.bucketname_m)
            
            
        except Exception as ex:
            jsonfile['errorDescription'] = str(ex)
            jsonfile['status'] = "FAIL"

        finally:
            try:
                #removing the input folder
                if path.exists(intput_dir_image):
                    shutil.rmtree(intput_dir_image)
                collection.insert_one(jsonfile)
            
            except Exception as ex:
                jsonfile = collection.insert_one({'_id':str(ObjectId()),'ErrorDescription':str(ex), 'Status':"FAIL"})
                abort(400)
            return jsonfile

api.add_resource(PlantGrowth, "/PlantGrowth")

if __name__ == '__main__':
    app.run(port=5000, debug='TRUE')
