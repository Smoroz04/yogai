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
            self.calculateAngle(self.get_point(11, lmlist), self.get_point(13, lmlist), self.get_point(15, lmlist)),  # left elbow
            self.calculateAngle(self.get_point(12, lmlist), self.get_point(14, lmlist), self.get_point(16, lmlist)),  # right elbow
            self.calculateAngle(self.get_point(23, lmlist), self.get_point(25, lmlist), self.get_point(27, lmlist)),  # left knee
            self.calculateAngle(self.get_point(24, lmlist), self.get_point(26, lmlist), self.get_point(28, lmlist)),  # right knee
            self.calculateAngle(self.get_point(13, lmlist), self.get_point(11, lmlist), self.get_point(23, lmlist)),  # left shoulder
            self.calculateAngle(self.get_point(14, lmlist), self.get_point(12, lmlist), self.get_point(24, lmlist))   # right shoulder
        ]


    def get_point(self, idx, lmlist):
        return (lmlist[idx][1], lmlist[idx][2]) if idx in range(len(lmlist)) else (0, 0)



    def checkPose(self, quickTimer, currAngles, wantedPose, frameCounter,currColor):
        THRESHOLD = 10

        if frameCounter % 5 == 0:
            incorrect_pose = False
            for i in range(len(currAngles)):
                if(i < len(currAngles) and i < len(wantedPose)):
                    print("CurrAngles:",currAngles[i],"WantedPose: ",wantedPose[i])
                    if abs(currAngles[i] - float(wantedPose[i])) > THRESHOLD:
                        incorrect_pose = True
                        break  
            if incorrect_pose:
                # If theres an incorrect post AND 
                # the quick timer is longer that two 
                # seconds(Meaning that the person is 
                # in the wrong pose for more than 2 seconds)
                if (time.time() - quickTimer) > 2:
                    print("You are in the wrong pose")
                    # Returns true, with the quicktimer 
                    # thats more than 2 seconds and True 
                    # so that the color changes to red
                    return quickTimer, True, "red"
                else:
                    # if the timer is not longer that 2 seconds, 
                    # but they are still in the incorrect pose, 
                    # return the quicktimer and green as the color
                    print("This is returning the quick timer")
                    return quickTimer, False, "green"
            else:
                # The pose they are doing is good, 
                # so its green and the quick timer is restarted
                print("this is returning a new quick timer")
                return time.time(), False, "green"
        if (currColor == "green"):
            return quickTimer, False, "green"
        else:
            return quickTimer, True, "red"
    
        


    
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