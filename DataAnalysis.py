import csv
import numpy as np
import pandas as pd

def load_reference_pose(pose_name, filename="poseData.csv"):
    #Load the reference joint angles for a given pose from poseData.csv.
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == pose_name:
                return list(map(float, row[1:]))
    return None

def load_attempts(filename="joint_angles.csv"):
    #Load all recorded joint angle attempts from joint_angles.csv.
    attempts = []
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            attempts.append(list(map(float, row)))
    return attempts

def calculate_accuracy(attempts, reference_pose, threshold):
    
    accuracy_scores = []
    threshold = 10  # Acceptable angle deviation in degrees
    
    for attempt in attempts:
        if (abs(attempt[0] - reference_pose[0]) >= threshold) or abs(attempt[1] - reference_pose[1]) >= threshold or abs(attempt[2] - reference_pose[2]) >= threshold or abs(attempt[3] - reference_pose[3]) >= threshold or abs(attempt[4] - reference_pose[4]) >= threshold or abs(attempt[5] - reference_pose[5]) >= threshold:
            accuracy_scores.append(0)
        else: 
            accuracy_scores.append(1)
    return accuracy_scores

def body_accuracy(attempts, reference_pose, threshold):
    accuracy_upper = []
    accuracy_lower = []

    for attempt in attempts:
        # Upper: elbows and shoulders
        if all(abs(attempt[i] - reference_pose[i]) < threshold for i in [0, 1, 4, 5]):
            accuracy_upper.append(1)
        else:
            accuracy_upper.append(0)

        # Lower: knees
        if all(abs(attempt[i] - reference_pose[i]) < threshold for i in [2, 3]):
            accuracy_lower.append(1)
        else:
            accuracy_lower.append(0)

    lowerBodyScore = calculatePercentage(accuracy_lower)
    upperBodyScore = calculatePercentage(accuracy_upper)
    return [lowerBodyScore, upperBodyScore]




def calculatePercentage(accuracyScoreArray):
    counter = 0
    for eachAttempt in accuracyScoreArray:
        if eachAttempt == 1:
            counter += 1
    percentageAccuracy = (counter/ len(accuracyScoreArray)) * 100
    return percentageAccuracy
