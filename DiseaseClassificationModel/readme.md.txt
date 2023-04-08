### Description:
 Disease classification model uses the images and predicts the disease in plant. The output details are stored in MongoDB.

### Input File:
 Evaluate any format of image.

### Parameters:
 
 - ImagePath: Path to the input image
 - ModelPath: Path to the trained models
 - PlantID: Id associated to specific plant


### Docker (Linux):

- $ clone the repository
- $ cd DiseaseClassificationTrainedModel
- $ docker ps -a  (to find active and exited docker)
- $ docker -t build diseaseclassification:v1.0 .   ---to build the docker
- $ docker run -d -p 6001:6001 diseaseclassification:v1.0  --to run the docker
- Note: If this doesn't work use --no-cache flag in the build command.


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
