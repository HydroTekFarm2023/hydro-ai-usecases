from PIL import Image
from flask import Flask, request
from flask_restful import reqparse
from subprocess import check_output, STDOUT
from PIL import Image
import io
import requests
import os
import time
import random
from selenium import webdriver
from subprocess import check_output, STDOUT
from selenium.webdriver.chrome.options import Options

random.seed(0)


DRIVER_PATH = r'./chromedriver'

def set_chrome_options() -> None:
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options

def getFiles(path):
  return [name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))]

def fetch_image_urls(query:str, max_links_to_fetch:int, wd:webdriver, sleep_between_interactions:int=5):
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)    
    
    # build the google query
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    # load the page
    wd.get(search_url.format(q=query))

    image_urls = set()
    image_count = 0
    results_start = 0
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)
        
        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")
        
        for img in thumbnail_results[results_start:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception:
                continue

            # extract image urls    
            actual_images = wd.find_elements_by_css_selector('img.Q4LuWd')
            for actual_image in actual_images:
                if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                    image_urls.add(actual_image.get_attribute('src'))

            image_count = len(image_urls)

            if len(image_urls) >= max_links_to_fetch:
                print(f"Found: {len(image_urls)} image links, done!")
                image_urls = list(image_urls)[:max_links_to_fetch]
                break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            #time.sleep(30)
            return image_urls
            load_more_button = wd.find_element_by_css_selector(".Q4LuWd")
            if load_more_button:
                wd.execute_script("document.querySelector('.Q4LuWd').click();")

        # move the result startpoint further down
        results_start = len(thumbnail_results)

    return image_urls
    
def persist_image(folder_path:str,url:str,name):
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        image = image.resize((416,416))
        file_path = os.path.join(folder_path,name + '.jpg')
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
        print(f"SUCCESS - saved {url} - as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")

def search_and_download(search_term:str,driver_path:str,target_folder,number_images=300):
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    with webdriver.Chrome(executable_path=driver_path,options=set_chrome_options()) as wd:
        res = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=5)
    count = 1
    for elem in res:
        persist_image(target_folder,elem,search_term.split(" in ")[0]+str(count))
        count = count+1


def uploadDataset(dataset_name,folders,destination):
    uploadImg = "gsutil cp -r "+dataset_name+' gs://'+destination
    print(uploadImg)
    check_output(uploadImg, stderr=STDOUT, shell=True)




def downloadDataset(plant,diseases,dataset_name,n,target_path = r"./",destination="hydrotek2022/"):
    folders = []
    target_path = os.path.join(target_path,dataset_name)
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    for disease in diseases:
        plant = plant.lower()
        dataset_str = disease+" in "+plant
        disease = '_'.join(disease.split(' ')).lower()
        folder_name = '_'.join([plant,disease])
        image_target_folder =  os.path.join(target_path,folder_name)
        if not os.path.exists(image_target_folder):
            os.makedirs(image_target_folder)
        print(dataset_str)
        search_and_download(search_term = dataset_str,driver_path= DRIVER_PATH,target_folder=image_target_folder, number_images=n)
        folders.append(folder_name)
    uploadDataset(dataset_name,folders,destination)

#downloadDataset("strawberry",["Anthracnose","Leaf drop","Powdery mildew","Septoria leaf spot","healthy plant"],"strawberry-fungal", 10)



app_flask = Flask(__name__)
parser = reqparse.RequestParser()
parser.add_argument('plant', type=str, required=True, help="Enter plant name")
parser.add_argument('destination', type=str, required=True, help="Enter destination directory")
parser.add_argument('classes', type=str, required=True, help="Enter classes")
parser.add_argument('n', type=int, required=True, help="Enter number of images")


@app_flask.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    #response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    
    return response


@app_flask.route('/v1/scraping/', methods=['GET'])
def home():
    if request.method == 'GET' or request.method == 'POST':
        return "Scraping Server is running! Test"


@app_flask.route('/v1/scraping/dataset', methods=['GET', 'POST'])
def predict():
    if request.method == 'GET' or request.method == 'POST':
        args = request.args
        plant = args['plant']
        classes = args['classes'].split(",")
        dataset_name = plant+'-fungal'
        n = int(args['n'])
        destination = args['destination']
        downloadDataset(plant,classes,dataset_name, n, destination=destination)
        return "Success"


if __name__ == '__main__':
    app_flask.run(host='0.0.0.0',debug=True, port=5001)