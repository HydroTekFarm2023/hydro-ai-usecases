import warnings
warnings.filterwarnings("ignore")

import fastai
from fastai import *
from fastai.vision.all import *
import numpy as np
import PIL



def test(test_img_path,model_path):
    try:
        data = pd.DataFrame()
        disease_classifier = load_learner(model_path)
        pred_class,pred_idx,outputs= disease_classifier.predict(test_img_path)
        defaults.device = torch.device('cpu')
        img = PIL.Image.open(test_img_path)
        img.show()
        prediction = str(pred_class)
        data = pd.DataFrame(columns=['Prediction'])
        data = data.append({"Prediction":prediction}, ignore_index=True)
        result = data.to_dict()
        for key, value in result.items():
            for zero, comment in value.items():
                pred = comment
                return pred
    
        
    except Exception as ex:
        print("The exception Occured is: ", ex)
        error = str(ex)
        return error

    
    
    