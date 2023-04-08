# -*- coding: utf-8 -*-
"""hydrotek.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LE2XKFw8BpK7yIS5bPxAwmkvpWfaKadv
"""

# pip install plantcv
from datetime import datetime
from scipy.spatial import distance
import cv2
import numpy as np
from plantcv import plantcv as pcv
from scipy.spatial.distance import euclidean
from imutils import perspective
from imutils import contours
import numpy as np
import imutils
import cv2
#from google.colab.patches import cv2_imshow

# user decides system dutch/NFT
#system = 'NFT'


def test(test_img_path, system):
    try:
        # Reading images and converting to hsv
        image, path, filename = pcv.readimage(test_img_path)
        imghsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # Preprocessing and finding reference object in NFT system
        # Setting min and max area to find the square reference object and reject other unwanted contours
        if system == 'NFT':
            sensitivity = 10
            lower_white = np.array([0, 0, 255-sensitivity])
            upper_white = np.array([255, sensitivity, 255])
            mask2 = cv2.inRange(imghsv, lower_white, upper_white)
            cnts = cv2.findContours(
                mask2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            # cv2.imshow('',mask2)
            min_area = 100
            max_area = 1000
            for c in cnts:
                area = cv2.contourArea(c)
                if area > min_area and area < max_area:
                    # approximate the contour
                    peri = cv2.arcLength(c, True)
                    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                    # if our approximated contour has four points, then we
                    # can assume that we have found our screen
                    if len(approx) == 4:
                        x, y, w, h = cv2.boundingRect(approx)
                        mak = c
                        # print(mak)
                        cv2.rectangle(image, (x, y), (x+w, y+h),
                                      (0, 255, 0), 2)
                        # print(mak)
                        #print('square found')
                        # cv2.imshow('',image)
                        break

        # Preprocessing and finding reference object in dutch system
        # Setting min and max area to find the square reference object and reject other unwanted contours

        if system == 'dutch':
            sensitivity = 100
            lower_white = np.array([0, 0, 255-sensitivity])
            upper_white = np.array([255, sensitivity, 255])
            mask2 = cv2.inRange(imghsv, lower_white, upper_white)
            cnts = cv2.findContours(
                mask2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)
            # cv2.imshow('',mask2)
            min_area = 1000
            max_area = 5000
            for c in cnts:
                area = cv2.contourArea(c)
                if area > min_area and area < max_area:
                    # approximate the contour
                    peri = cv2.arcLength(c, True)
                    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                    # if our approximated contour has four points, then we
                    # can assume that we have found our screen
                    if len(approx) == 4:
                        x, y, w, h = cv2.boundingRect(approx)
                        mak = c
                        # print(mak)
                        cv2.rectangle(image, (x, y), (x+w, y+h),
                                      (0, 255, 0), 2)
                        # print(mak)
                        #print('square found')
                        # cv2.imshow('',image)
                        break

        # Preprocessing inorder to find all the green contours and then finding our major green contour which is closest to the ref object(sticker)
        # Read
        #img = cv2.imread("D:/All_roads/NFTtest2.jpg")
        # convert to hsv
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        # masking green
        mask = cv2.inRange(hsv, (36, 25, 25), (70, 255, 255))
        # slice the green
        imask = mask > 0
        green = np.zeros_like(image, np.uint8)
        green[imask] = image[imask]
        # extracting green
        s = pcv.rgb2gray_hsv(rgb_img=green, channel='s')
        # Threshold the Saturation image
        # Inputs:
        #   gray_img - Grayscale image data
        #   threshold- Threshold value (between 0-255)
        #   max_value - Value to apply above threshold (255 = white)
        #   object_type - 'light' (default) or 'dark'. If the object is lighter than the background then standard threshold is done.
        #                 If the object is darker than the background then inverse thresholding is done.
        s_thresh = pcv.threshold.binary(
            gray_img=s, threshold=50, max_value=255, object_type='light')
        # cv2.imshow('',s_thresh)
        cnts = cv2.findContours(s_thresh.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        # Remove contours which are not large enough
        cnts = [x for x in cnts if cv2.contourArea(x) > 100]
        # Finding plant on which our reference sticker is placed
        N = cv2.moments(c)
        if N["m10"] > 0:
            center_X1 = int(N["m10"] / N["m00"])
            center_Y1 = int(N["m01"] / N["m00"])
            contour_center1 = (center_X1, center_Y1)
            cv2.circle(image, contour_center1, 3, (0, 0, 0), 2)

        buildings = []
        for contour in cnts:
            # find center of each contour
            M = cv2.moments(contour)
            if M["m10"] > 0:
                center_X = int(M["m10"] / M["m00"])
                center_Y = int(M["m01"] / M["m00"])
                contour_center = (center_X, center_Y)
                # print(contour_center)
                #cv2.circle(img, contour_center, 3, (0,0,255), 2)
                # calculate distance to image_center
                distances_to_center = (distance.euclidean(
                    contour_center1, contour_center))
                buildings.append({'contour': contour, 'center': contour_center,
                                 'distance_to_center': distances_to_center})

        # sort the buildings
        sorted_buildings = sorted(
            buildings, key=lambda i: i['distance_to_center'])

        # find contour of closest building to center and draw it (blue)
        center_building_contour = sorted_buildings[0]['contour']
        cv2.drawContours(image, [center_building_contour], 0, (255, 0, 0), 2)

        # creates an approximate rectangle around contour
        x, y, w, h = cv2.boundingRect(center_building_contour)
        # new_img=img[y:y+h,x:x+w]

        # cv2.imshow('',og)
        # cv2.imshow('',s_thresh)
        # cv2.imshow('',img)
        # cv2.imshow('',new_img)
        # cv2.waitKey(0)

        # Finding extreme contours for our selected plant
        d = center_building_contour
        # determine the most extreme points along the contour
        extLeft = tuple(d[d[:, :, 0].argmin()][0])
        extRight = tuple(d[d[:, :, 0].argmax()][0])
        extTop = tuple(d[d[:, :, 1].argmin()][0])
        extBot = tuple(d[d[:, :, 1].argmax()][0])
        # print(extRight)
        # print(extLeft)
        #wide = euclidean(extRight, extLeft)/pixel_per_cm
        #hte = euclidean(extTop, extBot)/pixel_per_cm
        # print(wide)
        # print(hte)

        # draw the outline of the object, then draw each of the
        # extreme points, where the left-most is red, right-most
        # is green, top-most is blue, and bottom-most is teal
        cv2.drawContours(image, [d], -1, (0, 255, 255), 2)
        cv2.circle(image, extLeft, 8, (0, 0, 255), -1)
        cv2.circle(image, extRight, 8, (0, 255, 0), -1)
        cv2.circle(image, extTop, 8, (255, 0, 0), -1)
        cv2.circle(image, extBot, 8, (255, 255, 0), -1)
        # show the output image
        # cv2.imshow('',img)
        # cv2.waitKey(0)
        # Finding size of plant based on pixel_per_cm ratio(2 X 2 cm sticker)
        cnts = [c, d]
        ref_object = cnts[0]
        box = cv2.minAreaRect(ref_object)
        box = cv2.boxPoints(box)
        box = np.array(box, dtype="int")
        box = perspective.order_points(box)
        (tl, tr, br, bl) = box
        dist_in_pixel = euclidean(tl, tr)
        dist_in_cm = 2
        pixel_per_cm = dist_in_pixel/dist_in_cm
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Draw remaining contours
        for cnt in cnts:
            box = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(box)
            box = np.array(box, dtype="int")
            box = perspective.order_points(box)
            (tl, tr, br, bl) = box
            cv2.drawContours(
                image, [box.astype("int")], -1, (0, 255, 0), 2)
            mid_pt_horizontal = (
                tl[0] + int(abs(tr[0] - tl[0])/2), tl[1] + int(abs(tr[1] - tl[1])/2))
            mid_pt_verticle = (
                tr[0] + int(abs(tr[0] - br[0])/2), tr[1] + int(abs(tr[1] - br[1])/2))
            wid = euclidean(tl, tr)/pixel_per_cm
            ht = euclidean(tr, br)/pixel_per_cm
            cv2.putText(image, "{:.1f}cm".format(wid), (int(mid_pt_horizontal[0] - 15), int(mid_pt_horizontal[1] - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            cv2.putText(image, "{:.1f}cm".format(ht), (int(mid_pt_verticle[0] + 10), int(mid_pt_verticle[1])),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        # return ht
        return ht, wid, timestamp

    except Exception as ex:
        print("The exception Occured is: ", ex)
        error = str(ex)
        return error


# print(test('./HeightAnalysis/Hydro_Toms.jpg', 'dutch'))