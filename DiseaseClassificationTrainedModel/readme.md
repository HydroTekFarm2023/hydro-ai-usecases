### Description:
 Training the Disease classification model using the images folder and store the model to GCP. The output details are stored in MongoDB.

### Input File:
zip file for images

### Parameters:
 
 - ImagePath: Path to the input folder image
 - PlantType: Name of the plant to be trained
 - apitype: The type of API
 - CustomerDb: The name of the database which needs to be updated
 
### Docker (Linux):

- $ clone the repository
- $ cd DiseaseClassificationTrainedModel
- $ docker ps -a  (to find active and exited docker)
- $ docker -t build ModelTraining:v1.0 .     (to build the docker)
- $ docker run -d -p 6005:6005 odelTraining:v1.0   (to run the docker)
- Note: If this doesn't work use --no-cache flag in the build command.

### Curl Command:

```
curl -v "http://localhost:6005/modeltraining?ImagePath=google-images/try1.tar.gz&PlantType=mint&apitype=dev&CustomerDb=hydrotekaidb"
 
```
### Output:

```
{"_id":{"$oid":"6016101c00532a33887d7675"},
"plantType":"mint",
"ModelMonitor":[{
"modelpath":"gs://hydrotekai/DiseaseClassificationModel/mint/export4775db98-8660-11eb-98d9-0242ac110002.pkl",
"train_score":[{"epoch":{"$numberInt":"0"},
"train_loss":{"$numberDouble":"1.2813129425048828"},
"valid_loss":{"$numberDouble":"0.278529942035675"},
"accuracy":{"$numberDouble":"0.800000011920929"},
"time":"01:23"}],
"Timestamp":"2021-03-16 14:02:49",
"status":"SUCCESS"}],
"status":"SUCCESS"}
```
