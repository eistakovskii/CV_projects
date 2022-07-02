import cv2
import time
import numpy as np
import Hand_Tracking_Module as htm
import math

# from PyCaw
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

############################
wCam, hCam = 640, 480
############################

cap = cv2.VideoCapture()
# The device number might be 0 or 1 depending on the device and the webcam
cap.open(0, cv2.CAP_DSHOW)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.HandDetector(detectionCon = 0.7)

# PyCaw code # Source: https://github.com/AndreMiras/pycaw

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
# print('Volume range: ', volume.GetVolumeRange()) # NB Volume range = (-192.0, 0.0, 1.5) ; Max = 0.0 Min = -85
# volume.SetMasterVolumeLevel(0.0, None)

volRange = volume.GetVolumeRange()


minVol = float(-85)
maxVol = float(0)

vol = 0
volBar = 400
volPer = 0

while (True):
    success, img = cap.read()
    img = detector.findHands(img)
    
    lmlist = detector.findPosition(img, draw = False)
    if len(lmlist) != 0:
        # print(lmlist[4], lmlist[8])
        
        x1, y1 = lmlist[4][1], lmlist[4][2]
        x2, y2 = lmlist[8][1], lmlist[8][2]
        cx, cy = (x1 + x2)//2, (y1 + y2)//2
        
        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1,y1), (x2, y2), (255, 0, 255), 2)
        cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        # print(length) # max = 125 ; min = 15
        

        vol = float(np.interp(length, [15, 125], [minVol, maxVol])) # to transform to an appropriate ranges
        volBar = float(np.interp(length, [15, 125], [400, 150]))
        volPer = float(np.interp(length, [15, 125], [0, 100]))
        # print(vol)
        volume.SetMasterVolumeLevel(vol, None)
        if length < 40:
            cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
    
    # the volume bar
    cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)}%', (50, 430), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
    
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    
    
    cv2.putText(img, f'FPS:{int(fps)}', (10, 470), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
    
    cv2.imshow('Image', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

volume.SetMasterVolumeLevel(0.0, None)
