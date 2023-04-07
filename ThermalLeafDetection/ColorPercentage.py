import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

class DominantColors:

    CLUSTERS = None
    IMAGE = None
    COLORS = None
    LABELS = None

    def __init__(self, image, clusters=3):
        self.CLUSTERS = clusters
        self.IMAGE = image
        
        
    def dominantColors(self):
    
        #read image
        img = cv2.imread(self.IMAGE)
        
        #convert to rgb from bgr
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
        #reshaping to a list of pixels
        img = img.reshape((img.shape[0] * img.shape[1], 3))
        
        #save image after operations
        self.IMAGE = img
        
        #using k-means to cluster pixels
        kmeans = KMeans(n_clusters = self.CLUSTERS)
        kmeans.fit(img)
        
        #the cluster centers are our dominant colors.
        self.COLORS = kmeans.cluster_centers_
        
        #save labels
        self.LABELS = kmeans.labels_
        
        #returning after converting to integer from float
        return self.COLORS.astype(int)
    
    def plotHistogram(self):
       
        #labels form 0 to no. of clusters
        numLabels = np.arange(0, self.CLUSTERS+1)
       
        #create frequency count tables    
        (hist, _) = np.histogram(self.LABELS, bins = numLabels)
        hist = hist.astype("float")
        hist /= hist.sum()
        
       
        
        #appending frequencies to cluster centers
        colors = self.COLORS
        
        
        #descending order sorting as per frequency count
        colors = colors[(-hist).argsort()]
        hist = hist[(-hist).argsort()]
        
       
                
        #creating empty chart
        chart = np.zeros((50, 500, 3), np.uint8)
        start = 0
        
        colorcode = []
        #creating color rectangles
        for i in range(self.CLUSTERS):
            end = start + hist[i] * 500
            
            #getting rgb values
            r = colors[i][0]
            g = colors[i][1]
            b = colors[i][2]
            
            
            Hex = '#%02x%02x%02x' % (int(r), int(g), int(b))
            colorcode.append(Hex)
            colorcode1 = np.array(colorcode)
            #using cv2.rectangle to plot colors
            cv2.rectangle(chart, (int(start), 0), (int(end), 50), (r,g,b), -1)
            start = end
            
        for i in colorcode:
            print(i)
        
        #display chart
        plt.figure()
        plt.axis("off")
        plt.imshow(chart)
        plt.show()
        
        df = pd.DataFrame({"colorcode": colorcode1, "percent":hist*100})
        print(df)
        return colorcode1, hist, colorcode
    
      
img = '/content/drive/MyDrive/Hydrotek/1.png'
clusters = 5
dc = DominantColors(img, clusters)
colors = dc.dominantColors()
colorcodes_1, percent_1, colorcode = dc.plotHistogram()

colorcodes_1 = {
  "Red": ["#db4217","#ff6666","#ff4d4d","#ff3333","#ff1a1a","#ff0000","#e60000","#cc0000","#b30000"," #ff5c33","#ff471a","#ff3300","#e62e00"," #cc2900"],
  "Orange": ["#ffa366","#ff944d","#ff8533","#ff751a","#ff6600","#e65c00","#ffa64d","#ff9933","#ff8c1a","#ff8000","#e67300","#ffb84d","#ffad33","#ffa31a","#ff9900"],
  "Yellow": ["#ffe066","#ffdb4d","#ffd633","#ffd11a","ffcc00","#e6b800","#ffff80","#ffff66"," #ffff4d","#ffff33","#ffff1a","#ffff00","#ffff99"],
  # Add blue color (Healthy)
}


# Threshold should not be hardcoded. Should have default (0.2).

red_count = 0
yellow_count = 0
orange_count = 0

for i in colorcode:
    for j in percent_1:
        if j>0.2:
            if i in (colorcodes_1["Red"]):
                print('Red color was detected more than 20%')
                red_count += 1
        
for i in colorcode:
    for j in percent_1:
        if j>0.2:
            if i in (colorcodes_1["Yellow"]):
                print('Yellow was detected more than 20%')
                yellow_count += 1
        
        
for i in colorcode:
    for j in percent_1:
        if j>0.2:
            if i in (colorcodes_1["Orange"]):
                print('Orange was detected more than 20%')
                orange_count += 1


if red_count == 0:
  print("Red color not detected.")
if yellow_count == 0:
  print("Yellow color not detected.")
if orange_count == 0:
  print("Orange color not detected.")

