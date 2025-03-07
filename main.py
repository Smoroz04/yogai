from flask import Flask, Response
import cv2
import time
import poseModule  # Import the external pose module

app = Flask(__name__)
camera = cv2.VideoCapture(0)
detector = poseModule.poseManager()  # Use poseManager from poseModule

def generate_frames():
    wantedPose = [178.0,177.0,178.0,178.0,13.0,14.0]
    frameCounter = 0
    quickTimer = time.time()
    mainTimer = time.time()

    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            frame = cv2.flip(frame, 1)  
            frame = detector.findPose(frame)
            lmlist = detector.findPosition(frame, draw=False)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            currAngles = detector.get_joint_angles(lmlist)

            if time.time() - mainTimer < 30:
                frameCounter += 1
                quickTimer = detector.checkPose(quickTimer, currAngles, wantedPose, frameCounter)

@app.route('/video')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
