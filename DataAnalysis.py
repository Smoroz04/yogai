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
    """Calculate the accuracy of each attempt compared to the reference pose."""
    accuracy_scores = []
    THRESHOLD = 10  # Acceptable angle deviation in degrees
    
    for attempt in attempts:
        differences = np.abs(np.array(attempt) - np.array(reference_pose))
        accuracy = 100 - (np.mean(differences) / THRESHOLD * 100)
        accuracy = max(0, accuracy)  # Ensure score doesn't go below 0
        accuracy_scores.append(accuracy)
    
    return accuracy_scores

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
    
    accuracy_scores = calculate_accuracy(attempts, reference_pose)
    df = pd.DataFrame({"Attempt": range(1, len(accuracy_scores) + 1), "Accuracy (%)": accuracy_scores})
    print(df)
    df.to_csv("pose_accuracy_report.csv", index=False)
    print("Pose accuracy report saved as pose_accuracy_report.csv")

if __name__ == "__main__":
    main()
