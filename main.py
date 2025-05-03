from flask import Flask, Response, render_template, request
import cv2
import time
import poseModule
import pandas as pd
import csv

from werkzeug.utils import secure_filename
from poseAnalyzer import poseAnalyzer, pushToCSV
from flask import redirect, url_for
import os
import atexit
latest_uploaded_pose = None  


app = Flask(__name__)
pose_analyzer = poseAnalyzer()

def save_joint_angles_to_csv(currAngles, filename="joint_angles.csv"):
    """Append joint angles to a CSV file."""
    with open(filename, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(currAngles)

def generate_frames(poseName):
    camera = cv2.VideoCapture(0)
    detector = poseModule.poseManager()
    wantedPose = getPoseData(poseName)
    frameCounter = 0
    quickTimer = time.time()
    mainTimer = time.time()
    activeAttempt = True
    border_colour = (0, 0, 255)
    clearCSV("joint_angles.csv")
    currColor = "green"
    countDownDuration = 3

    while True:
        success, frame = camera.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        frame = detector.findPose(frame)
        lmlist = detector.findPosition(frame, draw=False)
        elapsed_time = time.time() - mainTimer

        # Countdown or session timer display
        elapsed_time_text = (
            f"Tracking will start in: {3 - elapsed_time:.0f}s"
            if elapsed_time < countDownDuration
            else f"Time: {(elapsed_time - countDownDuration):.0f}s"
        )

        height, width, _ = frame.shape
        thickness = 10
        cv2.rectangle(frame, (0, 0), (width, height), border_colour, thickness)
        cv2.putText(frame, elapsed_time_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2, cv2.LINE_AA)

        # Stream the frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        # Pose tracking starts after countdown
        if countDownDuration < elapsed_time <= 30:
            currAngles = detector.get_joint_angles(lmlist)
            if currAngles:
                save_joint_angles_to_csv(currAngles)
            frameCounter += 1
            quickTimer, changeBorder, currColor = detector.checkPose(
                quickTimer, currAngles, wantedPose, frameCounter, currColor)
            border_colour = (0, 0, 255) if changeBorder else (0, 255, 0)

        elif elapsed_time > 30:
            break

    camera.release()


                



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

def video_stream():
    pose_name = request.args.get('pose','mountainPose.png')
    return generate_frames(pose_name)

# USER UPLOAD IMAGE IMPL

@atexit.register
def cleanup_uploaded_pose():
    if latest_uploaded_pose:
        pose_path = os.path.join(UPLOAD_FOLDER, latest_uploaded_pose)
        try:
            if os.path.exists(pose_path):
                os.remove(pose_path)
                print(f"[Atexit Cleanup] Deleted image: {pose_path}")
            
            with open("poseData.csv", "r") as f:
                rows = [row for row in csv.reader(f) if row[0].strip() != latest_uploaded_pose.strip()]

            with open("poseData.csv", "w", newline='') as f:
                csv.writer(f).writerows(rows)
                print(f"[Atexit Cleanup] Deleted pose data for: {latest_uploaded_pose}")

        except Exception as e:
            print(f"[Atexit Cleanup Error] {e}")

UPLOAD_FOLDER = 'static/posePictures'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_pose():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            pose_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(pose_path)
            global latest_uploaded_pose
            latest_uploaded_pose = filename

            # Analyze the image
            angles = pose_analyzer.analyzePose(pose_path)
            if angles:
                pushToCSV(filename, angles)
                return redirect(url_for('video_feed', pose=filename))
            else:
                os.remove(pose_path)  # remove invalid pose image
                return "Pose could not be detected.", 400
    return render_template('upload.html')

@app.route('/index')
def start():
    return render_template('index.html')

@app.route('/choose')
def choose():
    return render_template('choose.html')

@app.route('/video')
def video_feed():
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/display')
def display():
    return render_template('display.html')

@app.route('/before')
def before():
    return render_template('before.html')

if __name__ == '__main__':
    app.run(debug=True)
