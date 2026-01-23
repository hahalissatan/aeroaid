import cv2
import numpy as np
from djitellopy import Tello
import time

# --- 1. CONFIGURATION ---
SAFE_ZONE = 30       # Sensitivity of the "Green" lock
STABLE_TIME = 1.5    # How long to hold steady for the "Mock Hook"

# --- 2. SETUP ---
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, parameters)

# Connect to Tello just for the camera stream
drone = Tello()
drone.connect()
drone.streamon()
time.sleep(2)
cap = cv2.VideoCapture("udp://0.0.0.0:11111", cv2.CAP_FFMPEG)

stable_start_time = None
test_complete = False

print("--- BENCH TEST MODE ---")
print("Move the drone by hand in front of Marker ID 0.")
print("Watch the screen for the Red/Green lock status.")
print("Press 'R' to reset the test | 'Q' to quit")

try:
    while True:
        ret, frame = cap.read()
        if not ret: continue

        img = cv2.resize(frame, (640, 480))
        center_x, center_y = 320, 240
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = detector.detectMarkers(gray)
        
        is_centered = False
        lr_speed = ud_speed = 0

        # Draw the crosshair (Target)
        cv2.line(img, (center_x-20, center_y), (center_x+20, center_y), (255, 255, 255), 2)
        cv2.line(img, (center_x, center_y-20), (center_x, center_y+20), (255, 255, 255), 2)

        if ids is not None and 0 in ids and not test_complete:
            idx = np.where(ids == 0)[0][0]
            c = corners[idx][0]
            m_x = int(np.mean(c[:, 0]))
            m_y = int(np.mean(c[:, 1]))

            # Calculate Error
            error_x = m_x - center_x
            error_y = center_y - m_y

            # Calculate Speed (What the drone WOULD do)
            lr_speed = int(error_x * 0.2)
            ud_speed = int(error_y * 0.2)

            # Check for Lock
            if abs(error_x) < SAFE_ZONE and abs(error_y) < SAFE_ZONE:
                is_centered = True
                if stable_start_time is None:
                    stable_start_time = time.time()
            else:
                is_centered = False
                stable_start_time = None

            # UI Feedback
            color = (0, 255, 0) if is_centered else (0, 0, 255)
            cv2.circle(img, (m_x, m_y), 15, color, -1)
            cv2.aruco.drawDetectedMarkers(img, corners, ids)
            
            # Show the speed commands the drone is "thinking"
            cv2.putText(img, f"CMD: [LR: {lr_speed}, FB: 0, UD: {ud_speed}, YAW: 0]", 
                        (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            if stable_start_time:
                timer = time.time() - stable_start_time
                cv2.putText(img, f"LOCKING: {timer:.1f}s", (10, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 3. MOCK MANEUVER TRIGGER
        if stable_start_time and (time.time() - stable_start_time > STABLE_TIME):
            print("\n!!! TRIGGER !!!")
            print("Action 1: Drone would move FORWARD 100cm now.")
            print("Action 2: Drone would move UP 50cm now.")
            test_complete = True
            stable_start_time = None 

        if test_complete:
            cv2.putText(img, "MISSION SUCCESS - PRESS R TO RESET", (50, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        cv2.imshow("AeroAid Bench Test", img)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('r'): # Reset the test
            test_complete = False
            print("Test Reset.")
        elif key == ord('q'):
            break

except Exception as e:
    print(f"Error: {e}")
finally:
    drone.streamoff()
    cv2.destroyAllWindows()