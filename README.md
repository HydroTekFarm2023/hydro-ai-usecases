### Description:

Plant Growth Measurement using the images to monitor growth. The output details are stored in MongoDB.  
 ['Task Details'](https://gitlab.com/hydrotek-ai-grp/hydro-ai-usecases/-/issues/9)

### Input File:

Plant images of the designated system(NFT or Dutch system).

### Parameters:

- ImagePath: Path to the input image
- PlantID: Id associated to specific plant

### Curl Command:

```
$ curl -v "http://localhost:6003/PlantGrowth?ImagePath=HeightAnalysis/NFTtest2.jpeg&system=NFT&PlantId=1&apitype=devtest&CustomerDb=hydrotekaidb"

```
