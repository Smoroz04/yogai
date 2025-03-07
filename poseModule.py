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

class Joint:
    def __init__(self, name, pointA, pointB, pointC):
        self.name = name
        self.pointA = pointA
        self.pointB = pointB
        self.pointC = pointC

        self.angle = self.calculateAngle(pointA, pointB, pointC)  # Fixed call
        self.faultTime = 0
    
    def __init__(self, name, pointA, pointB, pointC, time):
        self.name = name
        self.pointA = pointA
        self.pointB = pointB
        self.pointC = pointC

        self.angle = self.calculateAngle(pointA, pointB, pointC)  # Fixed call
        self.faultTime = time

    def calculateAngle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c) 


        ab = a - b 
        cb = c - b  

        cosine_angle = np.dot(ab, cb) / (np.linalg.norm(ab) * np.linalg.norm(cb))
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0)) 
        return np.floor(np.degrees(angle)) 


class PoseChecker:
    def __init__(self, landmarkList, targetAngleList):
        self.landmarks = {i: landmarkList[i][1:] for i in range(len(landmarkList))}

        # Define joints dynamically
        self.leftElbowAngle = Joint("leftElbow", self.landmarks[11], self.landmarks[13], self.landmarks[15])
        self.rightElbowAngle = Joint("rightElbow", self.landmarks[12], self.landmarks[14], self.landmarks[16])
        self.leftKneeAngle = Joint("leftKnee", self.landmarks[23], self.landmarks[25], self.landmarks[27])
        self.rightKneeAngle = Joint("rightKnee", self.landmarks[24], self.landmarks[26], self.landmarks[28])
        self.leftShoulderAngle = Joint("leftShoulder", self.landmarks[13], self.landmarks[11], self.landmarks[23])
        self.rightShoulderAngle = Joint("rightShoulder", self.landmarks[14], self.landmarks[12], self.landmarks[24])
       
        # Corrected indexing for target angles
        self.targetLeftElbowAngle = targetAngleList[0]
        self.targetRightElbowAngle = targetAngleList[1]
        self.targetLeftKneeAngle = targetAngleList[2]
        self.targetRightKneeAngle = targetAngleList[3]
        self.targetLeftShoulderAngle = targetAngleList[4]
        self.targetRightShoulderAngle = targetAngleList[5]
        
    def checkJoint(self, joint, frame_count):
        target_angle = getattr(self, f"target{joint.name}Angle", None)  # Change this line to something else. idk how we are storing or calling the data. this data tbh. 
        if target_angle is not None:
            diff = abs(joint.angle - target_angle)
            if diff > 10:
                joint.faultTime += 1 
                print(f"{joint.name} misaligned! Deviation: {diff} degrees")
        else:
            print(f"Target angle for {joint.name} not found")
