import cv2
from imutils import face_utils
import imutils
import numpy as np
import dlib
import face_recognition
import math
import matplotlib.pyplot as plt
import datetime
import tkinter as tk
from tkinter import messagebox
import mysql.connector


def update_overlay(blink_count, avg_blink_rate):
    overlay_label.config(text=f"Blink Count: {blink_count}\nAvg Blink Rate: {avg_blink_rate:.2f} blinks/min")

def insert_data(blink_count, avg_blink_rate):
    sql_query = "INSERT INTO blink_data (blink_count, avg_blink_rate) VALUES (%s, %s)"
    data = (blink_count, avg_blink_rate)
    db_cursor.execute(sql_query, data)
    db_connection.commit()


overlay_window = tk.Tk()
overlay_window.wm_attributes("-topmost", 1)
overlay_window.wm_attributes("-alpha", 0.7)
overlay_label = tk.Label(overlay_window, text="", font=("Helvetica", 16), fg="white", bg="black")
overlay_label.pack()

db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="stress_management"
)
db_cursor = db_connection.cursor()
db_cursor.execute("""
    CREATE TABLE IF NOT EXISTS blink_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        blink_count INT,
        avg_blink_rate FLOAT
    )
""")

dif = 1500
rate_cap = 120 + dif
font = cv2.FONT_HERSHEY_PLAIN

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_POS_FRAMES, rate_cap)
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
#
dist = lambda x1, y1, x2, y2: (x1 - x2) ** 2 - (y1 - y2) ** 2
blink_count = 0
away_count = 0
avg_blink_rate = 15
curr_blink_rate = 15
avg_EAR = 0.3
drowsiness_count = 0
time5 = datetime.timedelta(minutes=0, seconds=0, microseconds=0)
time10 = datetime.timedelta(minutes=0, seconds=0, microseconds=0)
ret_count = "face"
frame_no = 0
while True:
    _, frame = cap.read()
    frame_no += 1
    # print(frame_no)
    # frame = cv2.flip(frame, 1)
    # height, width, _ = frame.shape
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray, 1)
    # faces = face_utils.shape_to_np(faces)
    if bool(faces):
        cv2.putText(frame, str(len(faces)), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    # print(faces.left())
    for i in range(len(faces)):
        face = faces.pop()
        # x,y=face.left(),face.top()
        # x1,y1=face.right(),face.bottom()
        out = 1
        # cv2.rectangle(frame,(x,y),(x1,y1),(0,255,0),2)
        #     cv2.imshow("Frame", frame)
        landmarks = predictor(gray, face)

        left_eye_region = np.array([(landmarks.part(42).x, landmarks.part(42).y),
                                    (landmarks.part(43).x, landmarks.part(43).y),
                                    (landmarks.part(44).x, landmarks.part(44).y),
                                    (landmarks.part(45).x, landmarks.part(45).y),
                                    (landmarks.part(46).x, landmarks.part(46).y),
                                    (landmarks.part(47).x, landmarks.part(47).y),
                                    ], np.int32)
        right_eye_region = np.array([(landmarks.part(36).x, landmarks.part(36).y),
                                     (landmarks.part(37).x, landmarks.part(37).y),
                                     (landmarks.part(38).x, landmarks.part(38).y),
                                     (landmarks.part(39).x, landmarks.part(39).y),
                                     (landmarks.part(40).x, landmarks.part(40).y),
                                     (landmarks.part(41).x, landmarks.part(41).y),
                                     ], np.int32)
        # cv2.polylines(frame, [left_eye_region], True, (0, 0, 255), 2)
        # cv2.polylines(frame, [right_eye_region], True, (0, 255, 0), 2)
        height, width, _ = frame.shape
        mask = np.zeros((height, width), np.uint8)
        mask2 = np.zeros((height, width), np.uint8)
        # cv2.polylines(mask, [left_eye_region], True, 255, 2)
        cv2.fillPoly(mask, [left_eye_region], 255)
        cv2.fillPoly(mask2, [right_eye_region], 255)

        left_eye = cv2.bitwise_and(gray, gray, mask=mask)
        right_eye = cv2.bitwise_and(gray, gray, mask=mask2)

        min_x = np.min(left_eye_region[:, 0])
        max_x = np.max(left_eye_region[:, 0])
        min_x2 = np.min(right_eye_region[:, 0])
        max_x2 = np.max(right_eye_region[:, 0])

        min_y = np.min(left_eye_region[:, 1])
        max_y = np.max(left_eye_region[:, 1])
        min_y2 = np.min(right_eye_region[:, 1])
        max_y2 = np.max(right_eye_region[:, 1])

        gray_eye = left_eye[min_y - 5:max_y + 5, min_x - 5:max_x + 5]
        gray_eye = cv2.GaussianBlur(gray_eye, (3, 3), 0)
        threshold_eye = cv2.adaptiveThreshold(gray_eye, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 103,
                                              -25)
        threshold_eye = cv2.flip(threshold_eye, 1)

        gray_eye2 = left_eye[min_y - 5:max_y + 5, min_x - 5:max_x + 5]
        gray_eye2 = cv2.GaussianBlur(gray_eye2, (3, 3), 0)
        threshold_eye2 = cv2.adaptiveThreshold(gray_eye2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 103,
                                               -25)
        threshold_eye2 = cv2.flip(threshold_eye2, 1)

        # threshold_eye = cv2.flip(threshold_eye, 1)
        height, width = threshold_eye.shape
        height2, width2 = threshold_eye2.shape

        left_side_thresh = threshold_eye[0:height, 0:int(width / 2)]
        left_side_white = cv2.countNonZero(left_side_thresh)
        left_side_thresh2 = threshold_eye2[0:height2, 0:int(width2 / 2)]
        left_side_white2 = cv2.countNonZero(left_side_thresh2)

        right_side_thresh = threshold_eye[0:height, int(width / 2):width]
        right_side_white = cv2.countNonZero(right_side_thresh)
        right_side_thresh2 = threshold_eye2[0:height2, int(width2 / 2):width2]
        right_side_white2 = cv2.countNonZero(right_side_thresh2)

        if left_side_white == 0:
            gaze_ratio1 = 1
        elif right_side_white == 0:
            gaze_ratio1 = 0
        else:
            gaze_ratio1 = left_side_white / right_side_white

        if left_side_white2 == 0:
            gaze_ratio2 = 1
        elif right_side_white2 == 0:
            gaze_ratio2 = 0
        else:
            gaze_ratio2 = left_side_white2 / right_side_white2

        gaze_ratio = (gaze_ratio1 + gaze_ratio2) / 2

        cv2.putText(frame, str(gaze_ratio), (50, 100), font, 2, (0, 0, 255), 3)

        if 0.95 < gaze_ratio < 1.25:
            cv2.putText(frame, "center", (50, 200), font, 2, (0, 0, 255), 3)
            away_count = 0
        elif 1.25 <= gaze_ratio or gaze_ratio <= 0.95:
            cv2.putText(frame, "away", (50, 200), font, 2, (0, 0, 255), 3)
            away_count += 1
        if away_count > 90:
            messagebox.showinfo("Alert", "Focus! get back to work")
            cv2.putText(frame, "focus", (300, 50), font, 2, (0, 255, 0), 3)
        blink_ratio = (math.sqrt((landmarks.part(47).x - landmarks.part(43).x) ** 2 + (landmarks.part(47).y - landmarks.part(43).y) ** 2) +
                       math.sqrt((landmarks.part(46).x - landmarks.part(44).x) ** 2 + (landmarks.part(46).y - landmarks.part(44).y) ** 2)) /\
                      (2 * math.sqrt((landmarks.part(45).x - landmarks.part(42).x)**2 + (landmarks.part(45).y-landmarks.part(42).y) ** 2))



        avg_EAR = (avg_EAR + blink_ratio)/2

        if avg_EAR < 0.24:
            drowsiness_count += 1
        else:
            drowsiness_count = 0
        print(drowsiness_count)
        if drowsiness_count > 60:
            messagebox.showinfo("Alert", "You are sleepy take  a break!!")
            drowsiness_count = 0
            cv2.putText(frame, "sleepy", (300, 50), font, 2, (0, 255, 0), 3)

        if blink_ratio < 0.2 and drowsiness_count<5:
            blink_count += 1
        if blink_count%5 == 0 and blink_count%10 != 0:
            time = datetime.datetime.now()
            time5 = datetime.timedelta(minutes=time.minute, seconds=time.second, microseconds=time.microsecond)
        if blink_count%10 == 0:
            time = datetime.datetime.now()
            time10 = datetime.timedelta(minutes=time.minute, seconds=time.second, microseconds=time.microsecond)
            time_taken = time10-time5
            curr_blink_rate = (6/(time_taken.total_seconds()))*60
            avg_blink_rate = (avg_blink_rate + curr_blink_rate) / 2

        # if frame_no%50 == 0:
        update_overlay(blink_count, avg_blink_rate)
        overlay_window.update()
        if(frame_no%300 == 0):
            drowsiness_count = 0
            if avg_blink_rate>90:
                messagebox.showinfo("Alert", "Abnormal blink rate detected!! your stress level is too high.\n Take a break ")
                insert_data(blink_count, avg_blink_rate)
            if avg_blink_rate < 10:
                messagebox.showinfo("Alert", "Abnormal blink rate detected!! you are in danger of facing eye fatigue\n Take a break ")
                insert_data(blink_count, avg_blink_rate)

        cv2.putText(frame, str(blink_count), (50, 250), font, 2, (255, 0, 0), 3)
        cv2.putText(frame, str(avg_EAR), (50, 300), font, 2, (255, 0, 0), 3)

        # cv2.imshow("eye", threshold_eye)

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
overlay_window.destroy()