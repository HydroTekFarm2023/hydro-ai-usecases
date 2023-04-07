# This Python file uses the following encoding: utf-8
import re
from fastai.vision import *
from flask import Flask, request
from flask_restful import reqparse
from subprocess import check_output, STDOUT
import os
import pandas as pd
import shutil

import model_train

def trainModel(dataset, source_loc = "",dest_loc = "",epochs=1, from_scratch = True,weight_loc = None,model_name = None):
  try:  
    bucketName = source_loc
    dest = dest_loc
    datasetName = dataset
    dwnImg = "gsutil cp -r gs://"+bucketName+"/"+datasetName + " " + "./"
    print("Downloading images .........")
    check_output(dwnImg, stderr=STDOUT, shell=True)
    dataset_path = datasetName 
    print(dataset_path)    
    print(from_scratch)


    
    training_res = model_train.train(dataset_path,epochs,from_scratch,weight_loc,model_name)
    # print(weights_path,datafile)
    print(training_res)
      
    # print(new_weights_path)
    weights_path = dataset_path + "/export.pkl"
    datafile = dataset_path + "/history.csv"
    new_weights_path = dataset_path + "/" + datasetName + "-export.pkl"
    model_learning_path = dataset_path + '/models/model.pth'
    new_model_path = dataset_path + '/models/' + datasetName + '-model.pth'
    print("PKL file path",weights_path)
    print("Model PKL path : ",new_weights_path)
    os.rename(weights_path,new_weights_path) 
    uploadImg = "gsutil cp "+new_weights_path+" gs://"+dest
    print("Uploading .pkl file")
    check_output(uploadImg, stderr=STDOUT, shell=True)

    
    pth_upload_query = "gsutil cp "+new_model_path+" gs://"+dest

    os.rename(model_learning_path,new_model_path) 
    print("Uploading .pth file")

    check_output(pth_upload_query, stderr=STDOUT, shell=True)



    print("Old Pth file name",model_learning_path)
    print("Updated Pth file name",new_model_path)
    results = pd.read_csv(datafile)
    return results.to_dict('list')
    # return "Success"
  except:
    return ("Error Occured")
  
  finally:
    shutil.rmtree('./' + datasetName)	


app_flask = Flask(__name__)
parser = reqparse.RequestParser()
parser.add_argument('datasetName', type=str, required=True, help="Enter dataset name")
parser.add_argument('epochs', type=int, required=True, help="Enter number of epochs")
parser.add_argument('source_loc', type=str, required=True, help="Enter source")
parser.add_argument('dest_loc', type=str, required=True, help="Enter destination")
parser.add_argument('from_scratch', type=int, required=True, help="Enter from scratch value")
parser.add_argument('weight_loc', type=str, required=False,help='Enter the weight of the model')
parser.add_argument('model_name', type=str, required=False,help='Enter the name of the model')


@app_flask.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    #response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    
    return response



@app_flask.route('/v1/fungaltrainingautomation/', methods=['GET'])
def home():
    if request.method == 'GET' or request.method == 'POST':
        return "Fungal Training Automation Server is running!"


@app_flask.route('/v1/fungaltrainingautomation/train', methods=['GET', 'POST'])
def train_model():
    if request.method == 'GET' or request.method == 'POST':        
        args = request.args
        datasetName = args['datasetName']
        epochs = int(args["epochs"])
        source_loc = args["source_loc"]
        dest_loc = args["dest_loc"]
        from_scratch = int(args["from_scratch"])
        # weight_loc = args['weight_loc']
        # model_name = args['model_name'] 

        if(from_scratch == 1):
          from_scratch = True
        else:
          from_scratch = False
        print(from_scratch)
        weight_loc,model_name = None,None
        if 'weight_loc' in args.keys():
              weight_loc = args['weight_loc']
        if 'model_name' in args.keys():
              model_name = args['model_name']
        print(datasetName, source_loc,dest_loc,epochs,from_scratch,weight_loc,model_name)
        results = trainModel(datasetName, source_loc,dest_loc,epochs,from_scratch,weight_loc,model_name)
        return results

if __name__ == '__main__':
    app_flask.run(host='0.0.0.0',port=5001,debug=True)
