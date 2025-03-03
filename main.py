from flask import Flask, Response
import cv2
import mediapipe as mp
import poseModule


app = Flask(__name__)
camera = cv2.VideoCapture(0)
detector = poseModule.poseDetector()


def generate_frames():
   while True:
       success, frame = camera.read()
       if not success:
           break
       else:
            frame = cv2.flip(frame, 1)  # Flip the frame horizontally
            frame = detector.findPose(frame)
            lmlist = detector.findPosition(frame, draw=False) 
            print(lmlist)   
            ret, buffer = cv2.imencode('.jpg', frame)   
            frame = buffer.tobytes()  
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  


@app.route('/video')   
def video_feed():
   return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
   app.run(debug=True)


