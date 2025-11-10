import cv2
import numpy as np
import winsound  # For beep sound on Windows
import threading
import time

# Load the cascade classifiers for face and eye detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Initialize the camera and take the instance
cap = cv2.VideoCapture(0)

# Status marking for current state
sleep = 0
drowsy = 0
active = 0
status = ""
color = (0, 0, 0)

# Flag to control continuous beep sound
beep_flag = False
beep_thread = None

def beep_continuous():
    while beep_flag:
        winsound.Beep(1000, 1000)  # Beep at 1000 Hz for 1 second

def beep_multiple(times):
    for _ in range(times):
        winsound.Beep(1000, 500)  # Beep at 1000 Hz for 0.5 second
        time.sleep(0.5)

def start_continuous_beep():
    global beep_thread
    beep_flag = True
    if not beep_thread or not beep_thread.is_alive():
        beep_thread = threading.Thread(target=beep_continuous)
        beep_thread.start()

def stop_continuous_beep():
    global beep_flag
    beep_flag = False
    if beep_thread and beep_thread.is_alive():
        beep_thread.join()

def compute(ptA, ptB):
    dist = np.linalg.norm(ptA - ptB)
    return dist

def blinked(eyes):
    # If eyes are detected, check if they're open or closed
    if len(eyes) == 0:
        return 0
    elif len(eyes) == 1:
        return 1
    else:
        return 2

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]

        eyes = eye_cascade.detectMultiScale(roi_gray)
        left_blink = blinked(eyes)
        right_blink = blinked(eyes)

        if left_blink == 0 or right_blink == 0:
            sleep += 1
            drowsy = 0
            active = 0
            if sleep > 6:
                status = "SLEEPING !!!"
                color = (255, 0, 0)
                start_continuous_beep()
        elif left_blink == 1 or right_blink == 1:
            sleep = 0
            active = 0
            drowsy += 1
            if drowsy > 6:
                status = "Drowsy !"
                color = (0, 0, 255)
                stop_continuous_beep()
                threading.Thread(target=beep_multiple, args=(4,)).start()
        else:
            drowsy = 0
            sleep = 0
            active += 1
            if active > 6:
                status = "Active :)"
                color = (0, 255, 0)
                stop_continuous_beep()

        cv2.putText(frame, status, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (255, 0, 0), 2)

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1)
    if key == 27:  # Press ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
stop_continuous_beep()  # Ensure beep stops after the loop ends