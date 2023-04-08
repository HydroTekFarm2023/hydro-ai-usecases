# Analyze signal data in Thermal image
import os
from typing import Type
from matplotlib.pyplot import xcorr
import numpy as np
from plantcv.plantcv import outputs
from plotnine import labs
from plantcv.plantcv.visualize import histogram
from plantcv.plantcv import deprecation_warning
from plantcv.plantcv._debug import _debug
from subprocess import check_output, STDOUT

import pymongo
from pymongo import MongoClient

import sys, traceback
import uuid
import cv2
import argparse
import string
from plantcv import plantcv as pcv


def analyze_thermal_values(thermal_array, mask, histplot=None, label="default"):
    """This extracts the thermal values of each pixel writes the values out to
       a file. It can also print out a histogram plot of pixel intensity
       and a pseudocolor image of the plant.

    Inputs:
    array        = numpy array of thermal values
    mask         = Binary mask made from selected contours
    histplot     = if True plots histogram of intensity values
    label        = optional label parameter, modifies the variable name of observations recorded

    Returns:
    analysis_image = output image

    :param thermal_array: numpy.ndarray
    :param mask: numpy.ndarray
    :param histplot: bool
    :param label: str
    :return analysis_image: ggplot
    """

    if histplot is not None:
        deprecation_warning("'histplot' will be deprecated in a future version of PlantCV. "
                            "This function creates a histogram by default.")

    # apply plant shaped mask to image and calculate statistics based on the masked image
    masked_thermal = thermal_array[np.where(mask > 0)]
    maxtemp = np.amax(masked_thermal)
    mintemp = np.amin(masked_thermal)
    avgtemp = np.average(masked_thermal)
    mediantemp = np.median(masked_thermal)

    hist_fig, hist_data = histogram(thermal_array, mask=mask, hist_data=True)

    bin_labels, hist_percent = hist_data['pixel intensity'].tolist(), hist_data['proportion of pixels (%)'].tolist()

    # Store data into outputs class
    outputs.add_observation(sample=label, variable='max_temp', trait='maximum temperature',
                            method='plantcv.plantcv.analyze_thermal_values', scale='degrees', datatype=float,
                            value=maxtemp, label='degrees')
    outputs.add_observation(sample=label, variable='min_temp', trait='minimum temperature',
                            method='plantcv.plantcv.analyze_thermal_values', scale='degrees', datatype=float,
                            value=mintemp, label='degrees')
    outputs.add_observation(sample=label, variable='mean_temp', trait='mean temperature',
                            method='plantcv.plantcv.analyze_thermal_values', scale='degrees', datatype=float,
                            value=avgtemp, label='degrees')
    outputs.add_observation(sample=label, variable='median_temp', trait='median temperature',
                            method='plantcv.plantcv.analyze_thermal_values', scale='degrees', datatype=float,
                            value=mediantemp, label='degrees')
    outputs.add_observation(sample=label, variable='thermal_frequencies', trait='thermal frequencies',
                            method='plantcv.plantcv.analyze_thermal_values', scale='frequency', datatype=list,
                            value=hist_percent, label=bin_labels)

    # change column names of "hist_data"
    hist_fig = hist_fig + labs(x="Temperature C", y="Proportion of pixels (%)")

   
    analysis_image = hist_fig
    # Store images
    outputs.images.append(analysis_image)

    return analysis_image, hist_data


def main(image, x, y, height, width):
    unique_id = str(uuid.uuid1())
    #gsutil -m cp gs://hydrotekai/thermal_images/cropped_leaf.jpg input_dir/cropped_leaf.jpg
    #print("Downloaded the images")
    #pcv.params.debug_outdir='/output_files/' #set output directory

    # Read raw thermal data

    # Inputs:
    #   filename - Image file to be read (possibly including a path)
    #   mode - Return mode of image ("native," "rgb,", "rgba", "gray", or "flir"), defaults to "native"
    #print("Figure 1. Original data as image.")
    thermal_data,path,filename = pcv.readimage(filename=image, mode="rgb")

    #print("Figure 2. Grayscale image.")
    gray = pcv.rgb2gray(rgb_img=thermal_data)

    # Rescale the thermal data to a colorspace with range 0-255

    # Inputs:
    #   gray_img - Grayscale image data 
    #   min_value - New minimum value for range of interest. default = 0
    #   max_value - New maximum value for range of interest. default = 255
    #print("Figure 3. Rescaled data image.")
    scaled_thermal_img = pcv.transform.rescale(gray_img=gray)
    


    # Threshold the thermal data to make a binary mask

    # Inputs:
    #   gray_img - Grayscale image data 
    #   threshold- Threshold value (between 0-255)
    #   max_value - Value to apply above threshold (255 = white) 
    #   object_type - 'light' (default) or 'dark'. If the object is lighter than the background then standard 
    #                 threshold is done. If the object is darker than the background then inverse thresholding is done. 
    #print("Figure 4. Binary mask from thresholding.")
    bin_mask = pcv.threshold.binary(gray_img=scaled_thermal_img, threshold=40, max_value=255, object_type='light')


    # Identify objects

    # Inputs: 
    #   img - RGB or grayscale image data for plotting 
    #   mask - Binary mask used for detecting contours 
    #print("Figure 5. Objects identified using the binary mask.")
    id_objects, obj_hierarchy = pcv.find_objects(img=thermal_data, mask=bin_mask)


    # Define the region of interest (ROI) 

    # Inputs: 
    #   img - RGB or grayscale image to plot the ROI on 
    #   x - The x-coordinate of the upper left corner of the rectangle 
    #   y - The y-coordinate of the upper left corner of the rectangle 
    #   h - The height of the rectangle 
    #   w - The width of the rectangle 
    #print("Figure 6. Region of interest drawn onto image.")
    roi, roi_hierarchy= pcv.roi.rectangle(img=thermal_data, x=x, y=y, h=height, w=width)


    # Decide which objects to keep

    # Inputs:
    #   img - RGB or grayscale image data to display kept objects on 
    #   roi_contour - contour of ROI, output from pcv.roi.rectangle in this case
    #   object_contour - Contour of objects, output from pcv.roi.rectangle in this case 
    #   obj_hierarchy - Hierarchy of objects, output from pcv.find_objects function
    #   roi_type - 'partial' (for partially inside, default), 'cutto', or 'largest' (keep only the largest contour)
    #print("Figure 7. Kept objects (green) drawn onto image.")
    roi_objects, hierarchy, kept_mask, obj_area = pcv.roi_objects(img=scaled_thermal_img,roi_contour=roi,
                                                                  roi_hierarchy=roi_hierarchy,
                                                                  object_contour=id_objects,
                                                                  obj_hierarchy=obj_hierarchy, 
                                                                  roi_type='cutto')


    ##### Analysis #####

    # Analyze thermal data 

    # Inputs:
    #   img - Array of thermal values
    #   mask - Binary mask made from selected contours
    #   histplot - If True plots histogram of intensity values (default histplot = False)
    #   label - Optional label parameter, modifies the variable name of observations recorded 
    #print("Figure 8. Histogram of the thermal values.")
    analysis_img, hist_data = analyze_thermal_values(thermal_array=gray.astype(np.float64), mask=kept_mask, histplot=True, label="default")


    #print("...............................................")
    #print(hist_data)
    #print("...............................................")


    # Pseudocolor the thermal data 

    # Inputs:
    #     gray_img - Grayscale image data
    #     obj - Single or grouped contour object (optional), if provided the pseudocolored image gets 
    #           cropped down to the region of interest.
    #     mask - Binary mask (optional) 
    #     background - Background color/type. Options are "image" (gray_img, default), "white", or "black". A mask 
    #                  must be supplied.
    #     cmap - Colormap
    #     min_value - Minimum value for range of interest
    #     max_value - Maximum value for range of interest
    #     dpi - Dots per inch for image if printed out (optional, if dpi=None then the default is set to 100 dpi).
    #     axes - If False then the title, x-axis, and y-axis won't be displayed (default axes=True).
    #     colorbar - If False then the colorbar won't be displayed (default colorbar=True)
    pseudo_img = pcv.visualize.pseudocolor(gray_img = gray, mask=kept_mask, cmap='viridis', 
                                           min_value=31, max_value=35)

    # Write shape and thermal data to results file
    pcv.outputs.save_results(filename=("output" + "_" + unique_id + ".csv"), outformat="csv")

    filename="output" + "_" + unique_id + ".csv"
    return filename