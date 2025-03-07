import cv2
import mediapipe as mp
import time
import numpy as np
import csv



class poseManager():
    def __init__(self, mode=False, upBody=False, smooth=True, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(
            static_image_mode=self.mode,
            smooth_landmarks=self.smooth,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.results = None  

    def findPose(self, frame, draw=True):
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)  
        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(frame, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
        return frame 
    
    def findPosition(self, frame, draw=True):
        lmList = []
        if self.results and self.results.pose_landmarks:
            h, w, c = frame.shape  
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(frame, (cx, cy), 5, (255, 0, 0), cv2.FILLED)
        return lmList
    
    def calculateAngle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c) 


        ab = a - b 
        cb = c - b  

        cosine_angle = np.dot(ab, cb) / (np.linalg.norm(ab) * np.linalg.norm(cb))
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0)) 
        return np.floor(np.degrees(angle)) 

        
    def checkPose(self, Quickertimer, currAngles, wantedPose, frameCounter ): 
        if frameCounter % 5 ==  0: 
            for i in currAngles.length(): 
                if quickTimer > 5:
                    if (abs(currAngles[i] - wantedPose[i]) > THRESHOLD):
                        print("You are not in the right pose")
                        return quickTimer 
                    else:
                        quickTimer = timer.time()
                        return quickTimer
                else:
                    if not(abs(currAngles[i] - wantedPose[i]) > THRESHOLD):
                        quickTimer = timer.time()
                        return quickTimer
                return quickTimer