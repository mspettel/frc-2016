import cv2
import numpy
import math
import time
from networktables import *


# Handle old versions of opencv
# New versions return
if cv2.__version__.startswith('2'):
    find_contours = cv2.findContours
else:
    def find_contours(image, mode, method):
        return cv2.findContours(image, mode, method)[1:]


NetworkTable.setIPAddress("roborio-166-frc.local")
NetworkTable.setClientMode()
NetworkTable.initialize()


visionDataTable = NetworkTable.getTable("VisionDataTable") #Connect specifically to vision NetworkTable

while not visionDataTable.isConnected():
    time.sleep(.1)

print("We are Connected")

visionDataTable.putNumber("shooterAngle",45.0) #Define default values for Network Table Variables
visionDataTable.putNumber("xPosition",0.0)
print("Initialized Values")

def find_distance(x1,y1,x2,y2):
    root = math.sqrt(  ((x2 - x1) ** 2) + ((y2 - y1) ** 2)  )
    rootInt = int(root)
    return rootInt

def threshold_range(im, lo, hi):
    '''Returns a binary image if the values are between a certain value'''

    unused, t1 = cv2.threshold(im, lo, 255, type=cv2.THRESH_BINARY)
    unused, t2 = cv2.threshold(im, hi, 255, type=cv2.THRESH_BINARY_INV)
    return cv2.bitwise_and(t1, t2)
def findDistanceToTarget(width):
    #note that the width is multiplied by 2 because of resolution change on the image
    #this change allows the new resolution to fit with the correct model

    distance = (44.139 * math.exp((-0.012 * (2 * width))))
    return distance

def findAngle(distance):
    angle = (.1183*(distance **2 ) - (3.468 * distance) + 69.203)
    return angle;

vc = cv2.VideoCapture()

# Connect to Axis Camera
if not vc.open('http://10.1.66.11/mjpg/video.mjpg'):
    print "Could not connect to camera"
    exit(1)

while cv2.waitKey(10) <= 0:
    success, img = vc.read()
    if not success:
        print ("Failure")
        break


    cv2.imshow("Source", img)
    #image processing

    scale = 1.0  # whatever scale you want (was .1)

    img = (img * scale).astype(numpy.uint8)

    # Convert original color image to hsv image
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    h, s, v = cv2.split(hsv) #Split hsv image into hue/saturation/value images

   # h = threshold_range(h, 40, 110) #Isolate only the green in the image
   
    h = threshold_range(h, 50, 80)
    s = threshold_range(s, 150, 255)
    v = threshold_range(v, 20, 255)

    #h = threshold_range(h, 55, 69)
    #s = threshold_range(s, 200, 255)
    #v = threshold_range(v, 10, 50)

    threshold = cv2.bitwise_and(h, cv2.bitwise_and(s, v)) #Combine 3 thresholds into one final threshold image

    kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2), anchor=(1,1))

    morphed = cv2.morphologyEx(threshold, cv2.MORPH_CLOSE, kernal, iterations=5) #make threshold more solid

    contours, hierarchy = find_contours(morphed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_KCOS)
    simplecontours = [cv2.approxPolyDP (cnt, 5, True) for cnt in contours]

    # Change binary to color
    color = cv2.cvtColor(morphed, cv2.COLOR_GRAY2BGR)

    cv2.drawContours(color, simplecontours, -1, (0,0,255), thickness = 2)

    x = []
    y = []
    w = []
    h = []
    a = []
    maxArea = 0;
    maxAreaIndex = 0;

    for partCount, contour, in enumerate(simplecontours):
               (xtemp, ytemp, wtemp, htemp) = cv2.boundingRect(contour) #Determine x,y,w,h by drawing a rectangle on contour

               x.append(xtemp + (wtemp/2)) #put x,y,w,h for each particle in an array
               y.append(ytemp + (htemp/2))
               w.append(wtemp)
               h.append(htemp)
               a.append(wtemp * htemp)
               atemp = wtemp * htemp

               if (atemp > maxArea):
                   maxArea = atemp;
                   maxAreaIndex = partCount;


               #Keep in mind, x and y are the actual centers, but xtemp and ytemp is the upper left corner
               
               if(atemp > 750):
                   cv2.circle(color,(xtemp + (wtemp/2) ,ytemp + (htemp/2)),2,(0,255,0),thickness = -1)
                   tempstring = " (%d,%d)" % (x[maxAreaIndex], y[maxAreaIndex])
                   cv2.putText(color, tempstring, (xtemp + wtemp,ytemp + (htemp/2)), cv2.FONT_HERSHEY_PLAIN, 1, (255,0,255), thickness = 1)
                   cv2.putText(color, "%d" %(wtemp), (xtemp + (wtemp/2),ytemp + htemp + 30), cv2.FONT_HERSHEY_PLAIN, 1, (255,0,255), thickness = 1)
                   cv2.putText(color, "%d" %(htemp), (xtemp - 30 ,ytemp + (htemp/2)), cv2.FONT_HERSHEY_PLAIN, 1, (255,0,255), thickness = 1)
                   cv2.putText(color, "Distance To Target: %.2f" %(findDistanceToTarget((w[maxAreaIndex]))), (0,16), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,255),thickness = 1)
                   cv2.putText(color, "Angle: %d" % (findAngle(findDistanceToTarget((w[maxAreaIndex])))), (0,32), cv2.FONT_HERSHEY_PLAIN, 1, (0,255,255),thickness = 1)
                   visionDataTable.putBoolean("isLargeTargetFound", False)
                   visionDataTable.putNumber("xPosition", x[maxAreaIndex])
                   visionDataTable.putNumber("shooterAngle", findAngle(findDistanceToTarget((w[maxAreaIndex]))))
                   visionDataTable.putNumber("distanceToTarget", findDistanceToTarget(w[maxAreaIndex]))
                   visionDataTable.putNumber("shooterAngle", findAngle(findDistanceToTarget((w[maxAreaIndex]))))  
    cv2.imshow("Cameras are awesome :D", color)
