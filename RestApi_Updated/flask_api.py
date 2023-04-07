from flask import Flask, request
from flask_restful import Resource, Api, reqparse, abort
from flask import Response
from image_scrapping import fetch_image_urls
from image_scrapping import persist_image
from subprocess import check_output, STDOUT
import pymongo
import os
from datetime import datetime
import time
import uuid

from os import path
import selenium
from selenium import webdriver
import shutil

from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
api = Api(app)

options = webdriver.ChromeOptions()
options.add_argument('--headless')
# options.add_argument('window-size=1200x600')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
uuid=str(uuid.uuid1())
print(uuid)
path = os.getcwd()
class getGather(Resource):

    def __init__(self):
        self.reqparser = reqparse.RequestParser()
        #self.reqparser.add_argument( "Driverpath", type=str, required=True, help="Please provide driverpath")
        self.reqparser.add_argument( "Search", type=str, required=True, help="Please provide search term")
        self.reqparser.add_argument( "number_images", type=str, required=True, help="Please provide number of images")
        self.reqparser.add_argument( "outputdir", type=str, required=True, help="Please provide output dirrectory")
        self.reqparser.add_argument( "apitype", type=str, required=True, help="Please provide the API Type")
        self.reqparser.add_argument( "CustomerDb", type=str, required=True, help="Please provide the name to the customer database")
        #self.gsutil = "gsutil -m cp"

    def get(self):

        args = self.reqparser.parse_args()

        #self.driverpath = args['Driverpath']
        Query = args['Search']
        self.images = args['number_images']
        self.directory = args['outputdir']
        self.customerdb = args['CustomerDb']
        self.apitype = args['apitype']
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
        collection = client[self.customerdb].datagather
        #collection =db.datagather
        DRIVER_PATH ="/ImageScrapping/chromedriver"
        search_term = Query
        datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        def search_and_download(search_term:str,driver_path:str,target_path=self.directory,number_images=self.images):

            try:
                target_folder=os.path.join(target_path,'_'.join(search_term.lower().split(' ')))
                target_path=target_folder
                print(target_folder)
                if not os.path.exists(target_folder):
                    os.makedirs(target_folder)

                with webdriver.Chrome(chrome_options=options,executable_path=driver_path) as wd:
                    res = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=5)

                for elem in res:
                    persist_image(target_folder,elem)

                #count=collection.insert_one({'PlantType':Query,'Imagecount':self.images,'Timestamp':datetime_now,'StorageLocation':self.directory,"Status":"Success"})

            except:
                print("Error")

        try:
            search_and_download(search_term = Query,driver_path=DRIVER_PATH)

        except:
            print("cannot downlaod")

        try:


            #img_folder_path ="/ImageScrapping/Output"+"/"+Query
            #number = os.listdir(img_folder_path)


            os.system("tar -cvzf"+" "+Query+uuid+".tar.gz"+" "+self.directory+"/"+Query)
            #subprocess.call(['tar', '-czf', target_path,target_folder])
            #cmd_dwnld_image = "gsutil cp -r"+" "+Query+uuid+".tar.gz"+" "+"gs://hydrotekai/google-images/"
            #cmd_stdout_image = check_output(cmd_dwnld_image, stderr=STDOUT, shell=True)
            #number=os.system(ls+" "+self.directory+"/"+Query | wc -l)
            #print(number)
            count=collection.insert_one({'PlantType':Query,'Imagecount':self.images,'Timestamp':datetime_now,'StorageLocation':self.directory,"Status":"Success"})
            print("Success")

        except Exception as e:
                print("Eroor")



api.add_resource(getGather, "/gatherinfo")
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=6000, debug='TRUE')
#curl -v "http://localhost:6000/gatherinfo?Search=cat&number_images=25&outputdir=/ImageScrapping/Output&apitype=dev&CustomerDb=hydrotekaidb"
