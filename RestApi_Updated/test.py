from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
from keras.models import load_model
from flask import Response
from image_scrapping import fetch_image_urls
from image_scrapping import persist_image
from subprocess import check_output, STDOUT
import pymongo
import os
from datetime import datetime
import time

from os import path
import selenium
from selenium import webdriver
import shutil

from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
api = Api(app)


class getGather(Resource):

    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        self.reqparser.add_argument( "Driverpath", type=str, required=True, help="Please provide driverpath")
        self.reqparser.add_argument( "Search", type=str, required=True, help="Please provide search term")
        self.reqparser.add_argument( "number_images", type=str, required=True, help="Please provide number of images")
        self.reqparser.add_argument( "outputdir", type=str, required=True, help="Please provide output dirrectory")
        self.gsutil = "gsutil -m cp"

    def get(self):

        args = self.reqparser.parse_args()

        self.driverpath = args['Driverpath']
        Query = args['Search']
        self.images = args['number_images']
        self.directory = args['outputdir']
        client = pymongo.MongoClient("mongodb+srv://hydrotekai:Kansas2020!m@cluster0.x5wba.gcp.mongodb.net/hydrotekaidb?retryWrites=true&w=majority")
        db = client.get_database('hydrotekaidb')
        collection =db.datagather
        DRIVER_PATH = self.driverpath
        search_term = Query
        datetime_now = datetime.now()

        def search_and_download(search_term:str,driver_path:str,target_path=self.directory,number_images=self.images):

            try:
                target_folder = os.path.join(target_path,'_'.join(search_term.lower().split(' ')))

                if not os.path.exists(target_folder):
                    os.makedirs(target_folder)

                with webdriver.Chrome(executable_path=driver_path) as wd:
                    res = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=5)

                for elem in res:
                    persist_image(target_folder,elem)

                count=collection.insert({'PlantType':Query,'Imagecount':self.images,'Timestamp':datetime_now,'StorageLocation':self.directory,"Status":"Success"})

            except:
                print("Error")

        #try:
        search_and_download(search_term = Query,driver_path=self.driverpath)
            #count=collection.insert({'PlantType':Query,'Imagecount':self.images,'Timestamp':datetime_now,'StorageLocation':self.directory,"Status":"Success"})



        #    gsutil -m cp -r C:/Users/Reddy/Desktop/Rest/cdog/cat gs://hydrotekai/google-images/
        os.system("tar -cvzf"+" "+Query+".tar.gz"+" "+self.directory+"/"+Query)

        try:

            cmd_dwnld_image = self.gsutil + " "+self.directory+"/"+Query+".tar.gz" + " " +"gs://hydrotekai/google-images/"
            cmd_stdout_image = check_output(cmd_dwnld_image, stderr=STDOUT, shell=True)
            print("Success")

        except Exception as e:
                print("Eroor"+e)
        #except:

            #print("Error")
            #count=collection.insert({'PlantType':Query,'Imagecount':self.images,'Timestamp':datetime_now,'StorageLocation':self.directory,"Status":"Fail"})




api.add_resource(getGather, "/gatherinfo")
if __name__ == '__main__':
    app.run(port=8000, debug='TRUE')
#curl -v "http://localhost:8000/gatherinfo?Driverpath=C:/webdriver/chromedriver.exe&Search=butter&number_images=25&outputdir=C:/Users/Reddy/Desktop/Rest"
