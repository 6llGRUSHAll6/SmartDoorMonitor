import cv2
import numpy as np
import pyautogui

THRESHOLD = 70  #можно настроить под свою веб камеру
MIN_AREA = 5000         
REF_UPDATE_DELAY = 5    
 
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Ошибка: Камера не найдена!")
    exit()

def process_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (21, 21), 0)
    return blur

print("Наведите камеру на дверь и нажмите 'c' для калибровки")
while True:
    ret, frame = cap.read()
    if not ret:
        continue

    cv2.imshow("Calibrate", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        ref_frame = process_frame(frame)
        break

cv2.destroyWindow("Calibrate")

last_update = 0
door_open = False
previous_door_open = None

while True:
    ret, frame = cap.read()
    if not ret:
        continue
    current_frame = process_frame(frame)
    frame_diff = cv2.absdiff(ref_frame, current_frame)
    thresh = cv2.threshold(frame_diff, THRESHOLD, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    motion_detected = False
    for contour in contours:
        if cv2.contourArea(contour) > MIN_AREA:
            motion_detected = True
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
    if motion_detected:
        door_open = True
    else:
        if cv2.getTickCount()/cv2.getTickFrequency() - last_update > REF_UPDATE_DELAY:
            ref_frame = current_frame
            last_update = cv2.getTickCount()/cv2.getTickFrequency()
            door_open = False
    if door_open != previous_door_open and previous_door_open is not None:
        if door_open:
            pyautogui.hotkey('winleft', 'd')
    
    previous_door_open = door_open

    status = "Door: OPEN!" if door_open else "Door: closed"
    color = (0, 0, 255) if door_open else (0, 255, 0)
    cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.imshow("Door Monitor", frame)
    cv2.imshow("Difference", thresh)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        ref_frame = process_frame(frame)

cap.release()
cv2.destroyAllWindows()
