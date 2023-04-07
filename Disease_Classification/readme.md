### Description:
 Disease classification model uses the images and predicts the disease in plant. The output details are stored in MongoDB.

### Input File:
 Evaluate any format of image.

### Parameters:
 
 - ImagePath: Path to the input image
 - ModelPath: Path to the trained models
 

### Curl Command:

```
 curl -v "http://localhost:6001/diseaseclassification?ImagePath=rgb_images/test_septorial_lettuce.jpg&ModelPath=DiseaseClassificationModel/Lettuce/export.pkl&PlantId=8"
 

```
### Output:

```
{"_id":{"$oid":"6006317ad2dc1fef32e6a109"},
"plantId":"8",
"healthMonitor":[{"diseaseType":"lettuce_Septoria_blight"}],
"status":"SUCCESS"}

```
