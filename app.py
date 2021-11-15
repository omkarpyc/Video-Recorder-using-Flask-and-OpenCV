import datetime
import time
from threading import Thread

import cv2
from flask import Flask, render_template, Response, request

global rec_frame, switch, rec, out
switch = 1
rec = 0

app = Flask(__name__)

cam = cv2.VideoCapture(0)


def record(out):
    while (rec):
        time.sleep(0.05)
        out.write(rec_frame)


def genFrames():
    global out, capture, rec_frame
    while True:
        success, frame = cam.read()
        if success:
            if (rec):
                rec_frame = frame
                frame = cv2.putText(cv2.flip(frame, 1), "Rec...", (0, 25), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 4)
                frame = cv2.flip(frame, 1)

            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame, 1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass
        else:
            pass


@app.route('/requests', methods=['POST', 'GET'])
def recording():
    global switch, camera
    if request.method == 'POST':
        if request.form.get('rec') == 'Start/Stop Recording':
            global rec, out
            rec = not rec
            if (rec):
                now = datetime.datetime.now()
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter('vid_{}.avi'.format(str(now).replace(":", '')), fourcc, 20.0, (640, 480))
                thread = Thread(target=record, args=[out, ])
                thread.start()
            else:
                out.release()


    elif request.method == 'GET':
        return render_template('index.html')
    return render_template('index.html')


@app.route('/')
def stage():
    return render_template('index.html')


@app.route('/video')
def video():
    return Response(genFrames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
