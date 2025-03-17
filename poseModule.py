import cv2
import mediapipe as mp
import numpy as np
import time
import pandas as pd


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

    def get_joint_angles(self, lmlist):
        if not lmlist:
            return []

        return [
            self.calculateAngle(self.get_point(11, lmlist), self.get_point(13, lmlist), self.get_point(15, lmlist)),  # leftElbowAngle
            self.calculateAngle(self.get_point(12, lmlist), self.get_point(14, lmlist), self.get_point(16, lmlist)),  # rightElbowAngle
            self.calculateAngle(self.get_point(23, lmlist), self.get_point(25, lmlist), self.get_point(27, lmlist)),  # leftKneeAngle
            self.calculateAngle(self.get_point(24, lmlist), self.get_point(26, lmlist), self.get_point(28, lmlist)),  # rightKneeAngle
            self.calculateAngle(self.get_point(13, lmlist), self.get_point(11, lmlist), self.get_point(23, lmlist)),  # leftShoulderAngle
            self.calculateAngle(self.get_point(14, lmlist), self.get_point(12, lmlist), self.get_point(24, lmlist)),  # rightShoulderAngle
            self.calculateAngle(self.get_point(11, lmlist), self.get_point(23, lmlist), self.get_point(25, lmlist)),  # leftHipAngle
            self.calculateAngle(self.get_point(12, lmlist), self.get_point(24, lmlist), self.get_point(26, lmlist)),  # rightHipAngle
        ]

    def get_point(self, idx, lmlist):
        return (lmlist[idx][1], lmlist[idx][2]) if idx in range(len(lmlist)) else (0, 0)



    def checkPose(self, quickTimer, currAngles, wantedPose, frameCounter):
        THRESHOLD = 10

        if frameCounter % 5 == 0:
            incorrect_pose = False

            for i in range(len(currAngles)):
                print(time.time() - quickTimer)

                if(i < len(currAngles) and i < len(wantedPose)):
                    if abs(currAngles[i] - float(wantedPose[i])) > THRESHOLD:
                        incorrect_pose = True
                        print("You are not in the right pose")
                        break
                        
                    else:
                        print("u are doing the right pose")

            if incorrect_pose:
                if time.time() - quickTimer > 5:
                    print("Timed out attempt, sorry")
                    return time.time(), True, True
                else:
                    return quickTimer, False, False
            else:
                return time.time(), False, True
        return quickTimer, False, False
    
        


    
    # def checkPose(self, quickTimer, currAngles, wantedPose, frameCounter):
    #     THRESHOLD = 10  # Define a threshold for pose correctness

    #     if frameCounter % 5 == 0:
    #         for i in range(len(wantedPose)):
    #             print(time.time() - quickTimer)
    #             if time.time() - quickTimer > 5:
    #                 if abs(currAngles[i] - float(wantedPose[i])) > THRESHOLD:  # Convert to float
    #                     print("You are not in the right pose")
    #                     return quickTimer
    #                 else:
    #                     quickTimer = time.time()
    #                     return quickTimer
    #             else:
    #                 if (abs(currAngles[i] - float(wantedPose[i])) > THRESHOLD):  # Convert to float
    #                     quickTimer = time.time()
    #                     #print('YOu are in the correct pose')
    #                     return quickTimer

    #     return quickTimer