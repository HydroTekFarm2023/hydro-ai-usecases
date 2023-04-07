import tensorflow as tf
# physical_devices = tf.config.experimental.list_physical_devices('GPU')
# if len(physical_devices) > 0:
#     tf.config.experimental.set_memory_growth(physical_devices[0], True)
from absl import app, flags, logging
from absl.flags import FLAGS
import core.utils as utils
from core.config import cfg
from core.yolov4 import filter_boxes
from tensorflow.python.saved_model import tag_constants
from PIL import Image
import cv2
import numpy as np
from tensorflow.compat.v1 import ConfigProto
from tensorflow.compat.v1 import InteractiveSession
from subprocess import check_output, STDOUT
import os
from pymongo import MongoClient
from datetime import datetime

# Flask utils
# from flask import Flask, redirect, url_for, request, render_template
from flask import Flask, request

# from werkzeug.utils import secure_filename
# from gevent.pywsgi import WSGIServer
# from flask_restful import Resource, Api, reqparse, abort
from flask_restful import reqparse

app_flask = Flask(__name__)

parser = reqparse.RequestParser()
parser.add_argument('bucketName', type=str, required=True, help="Enter bucket name")
parser.add_argument('imageName', type=str, required=True, help="Enter Image Name")
parser.add_argument('customerDB', type=str, required=True, help="Enter Customer DB Name")
parser.add_argument("plantType", type=str, required=True, help="Please provide the path to the image")
parser.add_argument("apiType", type=str, required=True, help="Please provide the API Type")


imagePath = "./data/images/"
customerDb = ""
plantname = ""
jsonfile = {'plantName':"", 'pestPresent':False, 'Timestamp':"", 'status':"", 'err':""}
imageDest = ""

@app_flask.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'GET' or request.method == 'POST':
        try:
            global imagePath, customerDb, plantname, imageDest, jsonfile
            args = parser.parse_args()
            bucketName = args['bucketName']
            imageName = args['imageName']
            customerDb = args['customerDB']
            plantname = args['plantType']
            apitype = args['apiType']
            dwnImg = "gsutil cp gs://"+bucketName+"/"+imageName + " " + "./data/images"
            check_output(dwnImg, stderr=STDOUT, shell=True)

            imageDest = ""
            imageDest = imagePath + imageName

            # print("imagePath>>>", imageDest)
            try:
                app.run(main)
            except SystemExit:
                pass
        except Exception as ex:
            datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            jsonfile = {'plantName':plantname, 'pestPresent':False, 'Timestamp':datetime_now, 'status':"FAILED", 'err':str(ex)}


    return jsonfile


flags.DEFINE_string('framework', 'tf', '(tf, tflite, trt')
flags.DEFINE_string('weights', './checkpoints/custom-416',
                    'path to weights file')
flags.DEFINE_integer('size', 416, 'resize images to')
flags.DEFINE_boolean('tiny', False, 'yolo or yolo-tiny')
flags.DEFINE_string('model', 'yolov4', 'yolov3 or yolov4')
flags.DEFINE_list('images', './data/images/dog.jpg', 'path to input image')
flags.DEFINE_string('output', './detections/', 'path to output folder')
flags.DEFINE_float('iou', 0.45, 'iou threshold')
flags.DEFINE_float('score', 0.25, 'score threshold')
flags.DEFINE_boolean('dont_show', True, 'dont show image output')


def main(_argv):
    global jsonfile

    config = ConfigProto()
    config.gpu_options.allow_growth = True
    session = InteractiveSession(config=config)
    STRIDES, ANCHORS, NUM_CLASS, XYSCALE = utils.load_config(FLAGS)
    input_size = FLAGS.size
    # images = FLAGS.images

    images = [imageDest]

    # load model
    if FLAGS.framework == 'tflite':
            interpreter = tf.lite.Interpreter(model_path=FLAGS.weights)
    else:
            saved_model_loaded = tf.saved_model.load(FLAGS.weights, tags=[tag_constants.SERVING])

    # loop through images in list and run Yolov4 model on each
    for count, image_path in enumerate(images, 1):
        original_image = cv2.imread(image_path)

        if np.shape(original_image) == ():
            print("Img not loaded properly, please try again", original_image)
            break
        else:
            print("Img loaded properly", original_image)

        original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

        image_data = cv2.resize(original_image, (input_size, input_size))
        image_data = image_data / 255.

        images_data = []
        for i in range(1):
            images_data.append(image_data)
        images_data = np.asarray(images_data).astype(np.float32)

        if FLAGS.framework == 'tflite':
            interpreter.allocate_tensors()
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            print(input_details)
            print(output_details)
            interpreter.set_tensor(input_details[0]['index'], images_data)
            interpreter.invoke()
            pred = [interpreter.get_tensor(output_details[i]['index']) for i in range(len(output_details))]
            if FLAGS.model == 'yolov3' and FLAGS.tiny == True:
                boxes, pred_conf = filter_boxes(pred[1], pred[0], score_threshold=0.25, input_shape=tf.constant([input_size, input_size]))
            else:
                boxes, pred_conf = filter_boxes(pred[0], pred[1], score_threshold=0.25, input_shape=tf.constant([input_size, input_size]))
        else:
            infer = saved_model_loaded.signatures['serving_default']
            batch_data = tf.constant(images_data)
            pred_bbox = infer(batch_data)

            for key, value in pred_bbox.items():
                boxes = value[:, :, 0:4]
                pred_conf = value[:, :, 4:]

        boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
            boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
            scores=tf.reshape(
                pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
            max_output_size_per_class=50,
            max_total_size=50,
            iou_threshold=FLAGS.iou,
            score_threshold=FLAGS.score
        )
        x = valid_detections.numpy()

        print("Connected to MongoDb")

        username = os.getenv("MONGO_USER", default="hydrotekai")
        pwd = os.getenv("MONGO_PWD", default="Kansas2020!m")
        host = os.getenv("MONGO_HOST", default="cluster0.x5wba.gcp.mongodb.net")

        mongocmd = ("mongodb+srv://{}:{}@" + host + "/" + customerDb + "?retryWrites=false")
        client = MongoClient(mongocmd.format(username, pwd))
        col = client[customerDb].PestDetection

        if x > 0:
            try:
                resultfile = {}
                datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print("Updating the database, pest present")
                existing_plantname = col.find({"plantType":plantname})

                if existing_plantname.count() > 0:
                    resultfile = col.find_one_and_update({"plantType":plantname},
                                                       {'$push': {'healthMonitor':{'hmErrorDescription':"",'hmStatus':"",'isHealthy':"",'imageId':"" ,'pestPresent':True,
                                                                                  'Timestamp':datetime_now}}})
                else:
                    resultfile = col.insert_one({'customerId':"", 'systemType':"", 'plantType':plantname, 'plantId':"", 'plantCategory':"", 'apiType':"",
                                                 'customerDb':"", 'imagePath':"",
                                               'healthMonitor':[{'hmErrorDescription':"",'hmStatus':"",'isHealthy':"",'imageId':"" ,'pestPresent':True,
                                                                 'Timestamp':datetime_now, 'modelPath':""}],
                                               'status':'SUCCESS', 'errorDescription':""})
                print("Database Updated")
                jsonfile = {'plantName':plantname, 'pestPresent':True, 'timestamp':datetime_now, 'status':"SUCCESS", 'err':""}

            except Exception as ex:
                print("Exception occurred:", ex)
                resultfile = col.insert_one({'customerId':"", 'systemType':"", 'plantType':plantname, 'plantId':"", 'plantCategory':"", 'apiType':"",
                                             'customerDb':"", 'imagePath':"",
                                             'healthMonitor':[{'hmErrorDescription':"",'hmStatus':"",'isHealthy':"",'imageId':"" ,'pestPresent':False,
                                                               'Timestamp':datetime_now, 'modelPath':""}],
                                             'status':'FAILURE', 'errorDescription':str(ex)})

            finally:
                session.close()

        else:
            resultfile = {}
            try:
                datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print("Updating the database, pest not present")
                existing_plantname = col.find({"plantType":plantname})
                if existing_plantname.count() > 0:
                    resultfile = col.find_one_and_update({"plantType":plantname},
                                                         {'$push': {'healthMonitor':{'hmErrorDescription':"",'hmStatus':"",'isHealthy':"",'imageId':"" ,'pestPresent':False,
                                                                                     'Timestamp':datetime_now}}})
                else:
                    resultfile = col.insert_one({'customerId':"", 'systemType':"", 'plantType':plantname, 'plantId':"", 'plantCategory':"", 'apiType':"",
                                                 'customerDb':"", 'imagePath':"",
                                                 'healthMonitor':[{'hmErrorDescription':"",'hmStatus':"",'isHealthy':"",'imageId':"" ,'pestPresent':False,
                                                                   'Timestamp':datetime_now, 'modelPath':""}],
                                                 'status':'SUCCESS', 'errorDescription':""})
                print("Database Updated")
                jsonfile = {'plantName':plantname, 'pestPresent':False, 'Timestamp':datetime_now, 'status':"SUCCESS", 'err':""}

            except Exception as ex:
                print("Exception occurred:", ex)
                resultfile = col.insert_one({'customerId':"", 'systemType':"", 'plantType':plantname, 'plantId':"", 'plantCategory':"", 'apiType':"",
                                             'customerDb':"", 'imagePath':"",
                                             'healthMonitor':[{'hmErrorDescription':"",'hmStatus':"",'isHealthy':"",'imageId':"" ,'pestPresent':False,
                                                               'Timestamp':datetime_now, 'modelPath':""}],
                                             'status':'FAILURE', 'errorDescription':str(ex)})

            finally:
                session.close()


# Code to draw bounding box
        # pred_bbox = [boxes.numpy(), scores.numpy(), classes.numpy(), valid_detections.numpy()]
        # print(pred_bbox)
        # # read in all class names from config
        # class_names = utils.read_class_names(cfg.YOLO.CLASSES)
        #
        # # by default allow all classes in .names file
        # allowed_classes = list(class_names.values())
        #
        # # custom allowed classes (uncomment line below to allow detections for only people)
        # #allowed_classes = ['person']
        #
        # image = utils.draw_bbox(original_image, pred_bbox, allowed_classes = allowed_classes)
        #
        # image = Image.fromarray(image.astype(np.uint8))
        # if not FLAGS.dont_show:
        #     image.show()
        # image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
        # cv2.imwrite(FLAGS.output + 'detection' + str(count) + '.png', image)

if __name__ == '__main__':
    app_flask.run(debug=True)