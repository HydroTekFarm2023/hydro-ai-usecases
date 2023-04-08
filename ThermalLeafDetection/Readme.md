## Overview:
Processing the thermal image of the plants and identifyig the percentage of colors to detect the health of the plant. 

## Sample image:
![Image](https://gitlab.com/hydrotek-ai-grp/hydro-ai-usecases/-/blob/siddarthpatilgit-master-patch-24777/Images/ThermalImageLeafSample.png)

## RestAPI:
Training the Thermal leaf scanning using the images folder and store the model to GCP. The output details are stored in MongoDB.

### MongoDB Schema Layout.

```
{
    "_id":{"$oid":"60acfeb917812d1905d3805c"},
    "customerId":"",
    "stationId":"",
    "systemType":"",
    "plantType":"",
    "plantId":"",
    "plantCategory":"",
    "apiType":"",
    "customerdb":"",
    "imagePath":"",
    "healthMonitor":[{"imageId":"",
                    "isHealthy":"",
                    "diseaseType":"",
                    "redColorPercentage":"",
                    "blueColorPercentage":"",
                    "orangeColorPercentage":"",
                    "yellowColorPercentage":"",
                    "blackColorPercentage":"",
                    "greenColorPercentage":"",
                    "whiteColorPercentage":"",
                    "timestamp":"",
                    "hmStatus":"",
                    "hmErrorDescription":""}],
    "modelPath":"",
    "status":"",
    "errorDescription":"Sample"}
```

### Input File:
Evaluate any format of image.

### Parameters:

ImagePath: Path to the input folder image
PlantType: Name of the plant to be trained
apitype: The type of API
CustomerDb: The name of the database which needs to be updated

```
Curl Command:
curl -v "http://localhost:6005/modeltraining?ImagePath=google-images/try1.tar.gz&PlantType=mint&apitype=dev&CustomerDb=hydrotekaidb"
```
 

### Output:
