import cv2
import mediapipe as mp
import numpy as np

class poseAnalyzer():
    def __init__(self):
        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose()


    # Same thing Ayan wrote to find the pose of for the frame by frame but for the image im inputing. 
    def findPose(self, image, draw=True):
        imgRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(imgRGB)
        if results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(image, results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
        return image, results

    def getLandmarks(self, results, image_shape):
        if not results.pose_landmarks:
            return None
        h, w, _ = image_shape
        landmarks = {}
        for id, lm in enumerate(results.pose_landmarks.landmark):
            landmarks[id] = (int(lm.x * w), int(lm.y * h))
        return landmarks

    def calculateAngle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c) 

        # Finding the vectors
        ab = a - b 
        cb = c - b  

        # Gay ass dot product
        cosine_angle = np.dot(ab, cb) / (np.linalg.norm(ab) * np.linalg.norm(cb))
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0)) 
        return np.degrees(angle)

    def analyzePose(self, image_path):
        image = cv2.imread(image_path)
        image, results = self.findPose(image)

        landmarks = self.getLandmarks(results, image.shape)
        if not landmarks:
            print("Dafuq is this picture, there aint no pose in this shit")
            return None

        angles = {}
        try:
            angles["Right elbow"] = self.calculateAngle(
                landmarks[11], landmarks[13], landmarks[15]
            )
            angles["left elbow"] = self.calculateAngle(
                landmarks[12], landmarks[14], landmarks[16]
            )
            angles["Right Knee"] = self.calculateAngle(
                landmarks[23], landmarks[25], landmarks[27]
            )
            angles["Left Knee"] = self.calculateAngle(
                landmarks[24], landmarks[26], landmarks[28]
            )
            angles["Right shoulder"] = self.calculateAngle(
                landmarks[13], landmarks[11], landmarks[23]
            )
            angles["Left Shoulder"] = self.calculateAngle(
                landmarks[14], landmarks[12], landmarks[24]
            )
        except KeyError:
            print("error, this shit dont work")

        return angles

pose_analyzer = poseAnalyzer()
image_path = "mountainPose.png"
angles = pose_analyzer.analyzePose(image_path)
if angles:
    print("Angles:", angles)