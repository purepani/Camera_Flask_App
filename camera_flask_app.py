import datetime
import os
import sys
import time
from threading import Thread

import cv2
import numpy as np
from flask import Flask, Response, render_template, request
from skimage.morphology import skeletonize

global capture, rec_frame, original_frame, grey, switch, neg, face, rec, out, out2
capture = 0
grey = 0
red = 0
neg = 0
filter = 0
face = 0
skeleton = 0
switch = 1
rec = 0

# make shots directory to save pics
try:
    os.mkdir("./shots")
except OSError as error:
    pass

# Load pretrained face detection model

# instatiate flask app
app = Flask(__name__, template_folder="./templates")


camera = cv2.VideoCapture(0)


def record(out, out2):
    global rec_frame
    while rec:
        time.sleep(0.05)
        out.write(rec_frame)
        out2.write(original_frame)


def gen_frames():  # generate frame by frame from camera
    global out, capture, rec_frame, original_frame
    while True:
        success, frame = camera.read()
        original_frame = frame
        if success:
            if grey:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if red:
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                lower = np.array([160, 50, 50])
                upper = np.array([180, 255, 255])
                mask = cv2.inRange(hsv, lower, upper)
                frame = cv2.bitwise_and(frame, frame, mask=mask)
            if filter:
                frame[frame < 150] = 0
            if skeleton:
                frame = skeletonize(frame)
            if neg:
                frame = cv2.bitwise_not(frame)
            if capture:
                capture = 0
                now = datetime.datetime.now()
                p = os.path.sep.join(
                    ["shots", "shot_{}.png".format(str(now).replace(":", ""))]
                )
                cv2.imwrite(p, frame)

            if rec:
                rec_frame = frame
                frame = cv2.putText(
                    cv2.flip(frame, 1),
                    "Recording...",
                    (0, 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    4,
                )
                frame = cv2.flip(frame, 1)

            try:
                ret, buffer = cv2.imencode(".jpg", cv2.flip(frame, 1))
                frame = buffer.tobytes()
                yield (
                    b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )
            except Exception as e:
                pass

        else:
            pass


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/requests", methods=["POST", "GET"])
def tasks():
    global switch, camera
    if request.method == "POST":
        if request.form.get("click") == "Capture":
            global capture
            capture = 1
        elif request.form.get("grey") == "Grey":
            global grey
            grey = not grey
        elif request.form.get("red") == "Red":
            global red
            red = not red
        elif request.form.get("filter") == "Filter":
            global filter
            filter = not filter
        elif request.form.get("skeleton") == "Skeleton":
            global skeleton
            skeleton = not skeleton
        elif request.form.get("neg") == "Negative":
            global neg
            neg = not neg
        elif request.form.get("stop") == "Stop/Start":
            if switch == 1:
                switch = 0
                camera.release()
                cv2.destroyAllWindows()

            else:
                camera = cv2.VideoCapture(0)
                switch = 1
        elif request.form.get("rec") == "Start/Stop Recording":
            global rec, out, out2
            rec = not rec
            if rec:
                now = datetime.datetime.now()
                fourcc = cv2.VideoWriter_fourcc(*"XVID")
                out = cv2.VideoWriter(
                    "vid_{}.avi".format(str(now).replace(":", "")),
                    fourcc,
                    20.0,
                    (640, 480),
                )
                out2 = cv2.VideoWriter(
                    "vid_{}_unfiltered.avi".format(str(now).replace(":", "")),
                    fourcc,
                    20.0,
                    (640, 480),
                )
                # Start new thread for recording the video
                thread = Thread(
                    target=record,
                    args=[
                        out,
                        out2,
                    ],
                )
                thread.start()
            elif rec == False:
                out.release()

    elif request.method == "GET":
        return render_template("index.html")
    return render_template("index.html")


if __name__ == "__main__":
    app.run()

camera.release()
cv2.destroyAllWindows()
