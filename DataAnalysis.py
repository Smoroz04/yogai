import csv
import numpy as np
import pandas as pd

def load_reference_pose(pose_name, filename="poseData.csv"):
    """Load the reference joint angles for a given pose from poseData.csv."""
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == pose_name:
                return list(map(float, row[1:]))
    return None

def load_attempts(filename="joint_angles.csv"):
    """Load all recorded joint angle attempts from joint_angles.csv."""
    attempts = []
    with open(filename, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            attempts.append(list(map(float, row)))
    return attempts

def calculate_accuracy(attempts, reference_pose):
    
    accuracy_scores = []
    THRESHOLD = 10  # Acceptable angle deviation in degrees
    
    for attempt in attempts:
        if (abs(attempt[0] - reference_pose[0]) >= 10) or abs(attempt[1] - reference_pose[1]) >= 10 or abs(attempt[2] - reference_pose[2]) >= 10 or abs(attempt[3] - reference_pose[3]) >= 10 or abs(attempt[4] - reference_pose[4]) >= 10 or abs(attempt[5] - reference_pose[5]) >= 10:
            accuracy_scores.append(0)
        else: 
            accuracy_scores.append(1)
    return accuracy_scores

def calculatePercentage(accuracyScoreArray):
    counter = 0
    for eachAttempt in accuracyScoreArray:
        if eachAttempt == 1:
            counter += 1
    percentageAccuracy = (counter/ len(accuracyScoreArray)) * 100
    return percentageAccuracy

def main():
    pose_name = "WarriorPose.png"  # Change to the relevant pose name
    reference_pose = load_reference_pose(pose_name)
    
    if reference_pose is None:
        print(f"Error: Reference pose '{pose_name}' not found.")
        return
    
    attempts = load_attempts()
    if not attempts:
        print("Error: No recorded attempts found.")
        return
    
    percentageAccuracy = calculatePercentage(calculate_accuracy(attempts,reference_pose))
    print("This is the accuracy i hope it works! ", percentageAccuracy)

main()