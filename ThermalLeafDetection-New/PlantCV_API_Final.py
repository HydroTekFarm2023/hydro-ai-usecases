import PlantCV_Final
from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
from flask import Response
from subprocess import check_output, STDOUT
import pymongo
import os
from os import path
import shutil
from datetime import datetime
import uuid
import pandas as pd
import json
import pymongo
import dns
from pymongo import MongoClient
from bson import ObjectId
app = Flask(__name__)
api = Api(app)
uuid = str(uuid.uuid1())
print(uuid)
path = os.getcwd()


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class thermalAnalysis(Resource):
    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument(
            "ImagePath", type=str, required=True, help="Please provide the path to the image")
        self.reqparser.add_argument(
            "X", type=int, required=True, help="Please provide the X axis to the image for ROI", default=9)
        self.reqparser.add_argument(
            "Y", type=int, required=True, help="Please provide the Y axis to the image for ROI", default=10)
        self.reqparser.add_argument("Height", type=int, required=True,
                                    help="Please provide the Height axis to the image for ROI", default=170)
        self.reqparser.add_argument("Width", type=int, required=True,
                                    help="Please provide the Width axis to the image for ROI", default=201)
        self.reqparser.add_argument("Threshold", type=int, required=True,
                                    help="Please provide the Threshold temperature to compare with", default=20)
        self.reqparser.add_argument(
            "PlantType", type=str, required=True, help="Please provide the type of plant")
        self.reqparser.add_argument(
            "apitype", type=str, required=True, help="Please provide the API Type")
        self.reqparser.add_argument("CustomerDb", type=str, required=True,
                                    help="Please provide the name to the customer database")
        self.gsutil = "gsutil -m cp gs://"

    def get(self):
        args = request.args
        self.imagepath = args['ImagePath']
        self.x = int(args['X'])
        self.y = int(args['Y'])
        self.height = int(args['Height'])
        self.width = int(args['Width'])
        self.plantname = args['PlantType']
        self.customerdb = args['CustomerDb']
        self.apitype = args['apitype']
        datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        input_dir = "inputfiles" + "_" + uuid
        #extract_dir = "extractfiles"+str(uuid.uuid1())
        jsonfile = {}
        try:
            print("Connecting to MongoDB.")
            username = os.getenv("MONGO_USER", default="hydrotekai")
            pwd = os.getenv("MONGO_PWD", default="Kansas2020!m")
            host = os.getenv(
                "MONGO_HOST", default="cluster0.x5wba.gcp.mongodb.net")
            port = os.getenv("MONGO_PORT", default="27017")
            # mongocmd = ""
            if self.apitype == "dev" or self.apitype == "devtest":
                mongocmd = ("mongodb+srv://{}:{}@" + host + "/" +
                            self.customerdb + "?retryWrites=true&w=majority")
            else:
                mongocmd = ("mongodb://{}:{}@" + host + ":" + port +
                            "/" + self.customerdb + "?retryWrites=true&w=majority")
            client = MongoClient(mongocmd.format(username, pwd))

            




            col = client[self.customerdb].ThermalHealthDetection

            print("Connected to MongoDB.")
            # creating directory for input file
            os.mkdir(input_dir)
            # os.mkdir(extract_dir)
            # paths to input files
            imagepath_on_system = input_dir + "/" + \
                args['ImagePath'].split('/')[-1]
            # downloading input files
            print("yes")
            cmd_dwnld_image = self.gsutil + self.imagepath + " " + imagepath_on_system
            cmd_stdout_image = check_output(
                cmd_dwnld_image, stderr=STDOUT, shell=True)
            print("Downloaded the images")
            output_file_path = PlantCV_Final.main(
                image=imagepath_on_system, x=self.x, y=self.y, height=self.height, width=self.width)
            dataframe = pd.read_csv(output_file_path)
            mean_temp = dataframe.iloc[3]['value']

            print("Mean temperature of the plant is: ", mean_temp)
            health_status = ""

            col_treat = client[self.customerdb].get_collection("thermal-treatment").find({"plant": self.plantname}).limit(1)
            self.threshold = 100
            treatment = ""
            for c in col_treat:
                self.threshold = c['threshold']
                treatment = c['treatment']
            
            print("Output file saved at local")
            upload_file = "gsutil cp" + " " + output_file_path + " " + \
                "gs://hydrotekai/thermal_images/output_files/"+self.plantname+"/"
            cmd_stdout_model = check_output(
                upload_file, stderr=STDOUT, shell=True)
            print("Output file Uploaded to GCP")
            path_to_gcp = "gs://hydrotekai/thermal_images/output_files/" + \
                self.plantname+"/"+output_file_path

            analysis = {"output_file_path": path_to_gcp,
                        "mean_temperature": mean_temp,
                        "health_status": health_status,
                        "image": args['ImagePath'],
                        "timestamp": datetime_now,

                        "status": "SUCCESS"}

            if mean_temp > self.threshold:
                health_status = "Plant is not healthly"
                analysis['treatment'] = treatment
            else:
                health_status = "Plant is Healthly"
            print(health_status)
            analysis['health_status'] = health_status
            print("Updating the database")
            existing_plantname = col.find({"plantType": self.plantname})
            
            jsonfile = analysis
            c = 0
            for i in existing_plantname:
                c = c+1
            if c > 0:
                col.update_one({"plantType": self.plantname},
                               {'$push': {"ModelMonitor": analysis}})
                print("Updating existing record")
            else:
                col.insert_one({"plantType": self.plantname,
                                "ModelMonitor": [analysis],
                                "status": "SUCCESS"})
                print("Inserting new record")
            print("Database Updated")
        except Exception as ex:
            col.insert_one({"plantType": self.plantname, 'errorDescription': str(ex),
                            'Timestamp': datetime_now, 'status': 'FAIL'})
            print(ex)
            print("Database Updated")
        os.remove(imagepath_on_system)
        os.rmdir(input_dir)
        print("Deleted the created files from local")
        return (jsonfile)


@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    #response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    
    return response
api.add_resource(thermalAnalysis, "/thermalanalysis")
if __name__ == '__main__':
    app.run('0.0.0.0', 6005, threaded=True)
