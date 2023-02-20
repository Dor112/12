# from cv2 import cv
import cv2
import sys
import numpy as np

print
cv2.__version__

DICE_SIZE = 70
BLUR_FACTOR = 5
# RED_LOW_THRESHOLD = 255
MIN_PIP_AREA = 150


def resizeRect(rect, sizeFactor):
    return (rect[0], (rect[1][0] + sizeFactor, rect[1][1] + sizeFactor), rect[2])


from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2

# инициализация объекта для захвата картинки
camera = PiCamera()
rawCapture = PiRGBArray(camera)

# «прогрев» камеры
time.sleep(0.1)

# получаем изображение с камеры
camera.capture(rawCapture, format="bgr")
image = rawCapture.array


# отображаем картинку на экране и ждём нажатия любой клавиши
#cv2.imshow("13579", image)
cv2.waitKey(0)

camera.capture('/home/daily/Desktop/13579.jpg')



img = cv2.imread("13579.jpg")


### Threshold image

blurred = cv2.medianBlur(img, BLUR_FACTOR)

blue = cv2.split(blurred)[0]
green = cv2.split(blurred)[1]
red = cv2.split(blurred)[2]

# Fetch the dice contours using red threshold. invert.
diceblocks = cv2.threshold(red, 150, 255, 1)  #color of the ground
invdiceblocks = 255 - diceblocks[1]
##cv2.imshow("diceblocks",invdiceblocks)

# do a distance transform and normalize that so we can visualize and threshold it
pyramids = cv2.distanceTransform(invdiceblocks, 2, 3)
cv2.normalize(pyramids, pyramids, 0, 1.2, cv2.NORM_MINMAX)

# obtain markers for the watershed algorithm by thresholding
markers = cv2.threshold(pyramids, 0.8, 1, 0)[1]
##cv2.imshow("markers",markers)


bwImg = cv2.convertScaleAbs(markers * 255)

# capture those contours!
_, pyramids, hierarchy = cv2.findContours(bwImg.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
print(str(len(pyramids)) + " dice")

# fit a rotated rectangle on the distance transformed pyramid
for pyramid in pyramids:
    rect = cv2.minAreaRect(pyramid)
    # resize it to a certain dice size
    rect = resizeRect(rect, DICE_SIZE)

    floatBox = cv2.boxPoints(rect)
    intBox = np.int0(floatBox)
    bwImg = cv2.drawContours(bwImg, [intBox], 0, (255, 0, 0), -1)

    pts1 = floatBox
    a, b, c, d = cv2.boundingRect(intBox)
    pts2 = np.float32([[a, b], [a + c, b], [a, b + d], [a + c, b + d]])

    M = cv2.getPerspectiveTransform(pts1, pts2)
    dst = cv2.warpPerspective(bwImg, M, pts2.shape)

# capture those large contours!
_, contours, hierarchy = cv2.findContours(bwImg.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# filter out the pips, and then cut out those using the contour areas
pips = 255 - cv2.threshold(cv2.cvtColor(blurred, cv2.COLOR_RGB2GRAY), 200, 255, 1)[1]
onlypips = cv2.bitwise_and(bwImg, pips)
# cv2.imshow("onlypips", onlypips)
dice = cv2.cvtColor(onlypips, cv2.COLOR_GRAY2RGB)

dice_results = [0, 0, 0, 0, 0, 0 ]
wrongdice = 0



# look at each dice face and determine number of pips
for contour in contours:
    pips = 0

    # get the coordinates to cut out the dice face from the image
    # with only the pips
    rect = cv2.minAreaRect(contour)
    floatBox = cv2.boxPoints(rect)
    intBox = np.int0(floatBox)
    a, b, c, d = cv2.boundingRect(intBox)

    # cut out the dice face
    subimage = onlypips[b:b + d, a:a + c]
    # count the number of contours
    _, pip_contours, subhierarchy = cv2.findContours(subimage.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for pip in pip_contours:
        # count pips only if they are of a certain size
        if cv2.contourArea(pip) >= MIN_PIP_AREA:
            pips = pips + 1

    # log erroneous dice
    if pips > 6 or pips == 0:
        wrongdice = wrongdice + 1
       # print(pips)
    else:
        dice_results[pips - 1] = dice_results[pips - 1] + 1
        cv2.putText(dice, str(pips), (a, b - 5), 0, 1, (200, 40, 25)) #color of numbers

# print out the results
print(dice_results)

one = int(dice_results[0])*1
two = int(dice_results[1])*2
three = int (dice_results[2])*3
four = int (dice_results[3])*4
five = int (dice_results[4])*5
six = int (dice_results[5])*6
suma = one+two+three+four+five+six
print(suma)
# print(str(pips))
str(wrongdice) + " erroneous objects found."

cv2.drawContours(dice, contours, -1, (60, 25, 40), 1) #color of contures
cv2.imshow('Dice', dice)
cv2.imshow('Original', img)


# cv2.cvtColor(blurred, cv2.COLOR_RGB2GRAY))

def doCallbackTest(value):
    # newImg = cv2.adaptiveThreshold(newImg,255,1,0,13,value)

    tmpImg = red.copy()#maybe color of cube
    newImg = 255 - cv2.threshold(tmpImg, value, 255, 1)[1]  # cv2.threshold(src, thresh, maxval, type
    cv2.drawContours(tmpImg,contours,-1,(60,25,100),1)

    cv2.imshow('Dice', newImg)


#cv2.imshow('Original',tmpImg)

lowThreshold = 1
max_lowThreshold = 255

#cv2.namedWindow("Dice", 0)
#cv2.createTrackbar('Value','Dice',lowThreshold, max_lowThreshold, doCallbackTest)

# doCallback(lowThreshold)

cv2.waitKey(0)
cv2.destroyAllWindows()