import cv2
import numpy as np
from djitellopy import Tello
import time

# --- 1. CONFIGURATION ---
TARGET_WIDTH = 60    # Pixel width at 100cm distance
SPEED_LIMIT = 20     # Max speed for centering
SAFE_ZONE = 25       # How many pixels off-center is "close enough"
STABLE_TIME = 2.0    # How many seconds to stay centered before auto-hooking

# --- 2. SETUP ---
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, parameters)

drone = Tello()
drone.connect()
drone.streamon()
time.sleep(2)
cap = cv2.VideoCapture("udp://0.0.0.0:11111", cv2.CAP_FFMPEG)

is_flying = False
maneuver_complete = False
stable_start_time = None

print("T: Takeoff | L: Land | Q: Quit")

try:
    while True:
        ret, frame = cap.read()
        if not ret: continue

        img = cv2.resize(frame, (640, 480))
        center_x, center_y = 320, 240
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = detector.detectMarkers(gray)
        
        lr_speed = fb_speed = ud_speed = 0
        is_centered = False

        if ids is not None and 0 in ids and not maneuver_complete:
            idx = np.where(ids == 0)[0][0]
            c = corners[idx][0]
            m_x = int(np.mean(c[:, 0]))
            m_y = int(np.mean(c[:, 1]))
            current_width = np.linalg.norm(c[0] - c[1])

            # Calculate Errors
            error_x = m_x - center_x
            error_y = center_y - m_y
            error_z = TARGET_WIDTH - current_width

            # Centering Logic (P-Control)
            lr_speed = max(-SPEED_LIMIT, min(SPEED_LIMIT, int(error_x * 0.2)))
            ud_speed = max(-SPEED_LIMIT, min(SPEED_LIMIT, int(error_y * 0.2)))
            fb_speed = max(-SPEED_LIMIT, min(SPEED_LIMIT, int(error_z * 0.4)))

            # CHECK IF CENTERED
            if abs(error_x) < SAFE_ZONE and abs(error_y) < SAFE_ZONE and abs(error_z) < 10:
                is_centered = True
                if stable_start_time is None:
                    stable_start_time = time.time()
            else:
                is_centered = False
                stable_start_time = None

            # Visual Feedback
            color = (0, 255, 0) if is_centered else (0, 0, 255)
            cv2.aruco.drawDetectedMarkers(img, corners, ids)
            cv2.circle(img, (m_x, m_y), 10, color, -1)
            
            if stable_start_time:
                timer = time.time() - stable_start_time
                cv2.putText(img, f"LOCKING: {timer:.1f}s", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 3. AUTOMATIC MANEUVER TRIGGER
        if is_flying and stable_start_time and (time.time() - stable_start_time > STABLE_TIME):
            print(">>> TARGET LOCKED: AUTOMATIC HOOKING <<<")
            drone.send_rc_control(0, 0, 0, 0)
            time.sleep(1)
            drone.move_forward(50)
            time.sleep(1)
            drone.move_up(50)
            print(">>> ITEM SECURED <<<")
            maneuver_complete = True
            stable_start_time = None # Reset

        if is_flying:
            drone.send_rc_control(lr_speed, fb_speed, ud_speed, 0)

        cv2.imshow("AeroAid Auto-Mission", img)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('t'):
            drone.takeoff()
            is_flying = True
        elif key == ord('l'):
            drone.land()
            is_flying = False
        elif key == ord('q'):
            break

except Exception as e:
    print(f"Error: {e}")
finally:
    drone.land()
    drone.streamoff()
    cv2.destroyAllWindows()