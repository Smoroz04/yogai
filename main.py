from flask import Flask, Response, render_template, request
import cv2
import time
import poseModule  # Import the external pose module
import pandas as pd
import csv




app = Flask(__name__)
camera = cv2.VideoCapture(0)
detector = poseModule.poseManager()  # Use poseManager from poseModule

def save_joint_angles_to_csv(currAngles, filename="joint_angles.csv"):
    """Append joint angles to a CSV file."""
    with open(filename, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(currAngles)

def generate_frames(poseName):
    wantedPose = getPoseData(poseName)
    frameCounter = 0
    quickTimer = time.time()
    mainTimer = time.time()
    activeAttempt = True
    border_colour = (0, 0, 255)
    clearCSV("joint_angles.csv")
    currColor = "green"


    while True:
        # Open the camera
        success, frame = camera.read()
        if not success:
            break
        else:
            # opens on specific camera
            frame = cv2.flip(frame, 1)  
            # Gets the the specific frame 
            frame = detector.findPose(frame)
            # gets the pose dots from the frame and puts them into an array lmlist
            lmlist = detector.findPosition(frame, draw=False)
            
            # Gets how long its been since the start of the time
            elapsed_time = time.time() - mainTimer

            # idk what the point of this is tbh
            elapsed_time_text = f"Time: {elapsed_time:.0f}s"  


            height, width, _ = frame.shape
            thickness = 10

            cv2.rectangle(frame, (0,0), (width, height), border_colour, thickness)

            cv2.putText(frame, elapsed_time_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                        1, (0, 255, 0), 2, cv2.LINE_AA)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            if elapsed_time <= 30:
                currAngles = detector.get_joint_angles(lmlist)
                if currAngles:
                    save_joint_angles_to_csv(currAngles)
                frameCounter += 1
                quickTimer, changeBorder, currColor = detector.checkPose(quickTimer, currAngles, wantedPose, frameCounter, currColor)
                if (changeBorder):
                    # go to red
                    border_colour = (0,0,255)
                else:
                    # Go Green
                    border_colour = (0,255,0)
            else:
                exit
                
            


def clearCSV(csvName):
    fileName = csvName
    f = open(fileName, "w")
    f.truncate()
    f.close()

def getPoseData(poseName):
    with open('poseData.csv', mode='r') as csv_data:
        reader = csv.reader(csv_data, delimiter=",")
        for row in reader:
            if row[0] == poseName:
                return row[1:]
    return None


@app.route('/index')
def start():
    return render_template('index.html')

@app.route('/choose')
def choose():
    return render_template('choose.html')
         
@app.route('/video')
def video_feed():
    pose_name = request.args.get('pose', 'mountainPose.png')
    return Response(generate_frames(pose_name), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/display')
def display():
    return render_template('display.html')

if __name__ == '__main__':
    app.run(debug=True)
