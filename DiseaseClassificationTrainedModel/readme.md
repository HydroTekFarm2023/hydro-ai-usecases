### Description:
 Training the Disease classification model using the images folder and store the model to GCP. The output details are stored in MongoDB.

### Input File:
 Evaluate any format of image.

### Parameters:
 
 - ImagePath: Path to the input folder image
 - PlantType: Name of the plant to be trained
 - apitype: The type of API
 - CustomerDb: The name of the database which needs to be updated
 
 

### Curl Command:

```
curl -v "http://localhost:6005/modeltraining?ImagePath=google-images/try1.tar.gz&PlantType=mint&apitype=dev&CustomerDb=hydrotekaidb"
 
```
### Output:

```

```