# %autoreload 2
# %matplotlib inline
import warnings
warnings.filterwarnings("ignore")
import os
import fastai
from fastai import *
from fastai.vision.all import *
from fastai.metrics import error_rate, FBeta
from fastai.callback.core import *

def test(train_img_path):
    try:
        data = ImageDataLoaders.from_folder(path=train_img_path,
                                  item_tfms=RandomResizedCrop(256, min_scale=0.5), 
                                  valid_pct=0.15,
                                  batch_tfms=aug_transforms(),
                                  size =256,
                                  bs=10,
                                  num_workers=0)
        classes = data.vocab
        #data.show_batch()

        #learn = cnn_learner(data,models.resnet50, loss_func=CrossEntropyLossFlat(), metrics= accuracy)
        
        #learn.fit_one_cycle(1, lr_max=slice(1e-4,1e-2), cbs=[SaveModelCallback(monitor="accuracy")])
        learn = cnn_learner(data, models.resnet50, metrics=accuracy, cbs=[CSVLogger, SaveModelCallback(monitor="accuracy")])
        learn.save("model")
        learn.fit_one_cycle(1,lr_max=slice(1e-4,1e-2))
        df = learn.csv_logger.read_log()
        a1 = df['accuracy'].max()
        target = df[df.isin([a1]).any(axis = 1)]
        learn.remove_cbs(CSVLogger)
        learn.export()
        
        return target
                
        #interpret = ClassificationInterpretation.from_learner(learn)
        #interpret.plot_confusion_matrix(figsize=(10,10), dpi=60)

        
        
        
    except Exception as ex:
        print("The exception Occured is: ", ex)
        error = str(ex)
        return error

if __name__ == '__main__':
    input1 = input()
    test(input1)