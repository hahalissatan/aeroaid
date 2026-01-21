import cv2
import numpy as np
from djitellopy import Tello
import time

# --- 1. ORIGINAL STEADY CONFIGURATION ---
SPEED_LIMIT = 20     # Back to original safe speed
SAFE_ZONE = 25       # Back to original precision zone
STABLE_TIME = 1.5    # Back to original stable wait time

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

print("READY: Start drone manually at the 50cm - 100cm mark.")
print("T: Takeoff | L: Land | Q: Quit")

try:
    while True:
        ret, frame = cap.read()
        if not ret: continue

        img = cv2.resize(frame, (640, 480))
        center_x, center_y = 320, 240
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        corners, ids, rejected = detector.detectMarkers(gray)
        
        lr_speed = ud_speed = 0
        is_centered = False

        # Only process if we see ID 0 and mission isn't finished
        if ids is not None and 0 in ids and not maneuver_complete:
            idx = np.where(ids == 0)[0][0]
            c = corners[idx][0]
            m_x = int(np.mean(c[:, 0]))
            m_y = int(np.mean(c[:, 1]))

            # Calculate Errors (X and Y only)
            error_x = m_x - center_x
            error_y = center_y - m_y

            # ORIGINAL SMOOTH GAINS (0.2)
            lr_speed = max(-SPEED_LIMIT, min(SPEED_LIMIT, int(error_x * 0.2)))
            ud_speed = max(-SPEED_LIMIT, min(SPEED_LIMIT, int(error_y * 0.2)))

            # Check if drone is centered in the safe zone
            if abs(error_x) < SAFE_ZONE and abs(error_y) < SAFE_ZONE:
                is_centered = True
                if stable_start_time is None:
                    stable_start_time = time.time()
            else:
                is_centered = False
                stable_start_time = None

            # Visual Feedback
            color = (0, 255, 0) if is_centered else (0, 0, 255)
            cv2.circle(img, (m_x, m_y), 10, color, -1)
            cv2.aruco.drawDetectedMarkers(img, corners, ids)
            
            if stable_start_time:
                timer = time.time() - stable_start_time
                cv2.putText(img, f"STABILIZING: {timer:.1f}s", (10, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # 3. AUTOMATIC HOOKING TRIGGER
        if is_flying and stable_start_time and (time.time() - stable_start_time > STABLE_TIME):
            print(">>> TARGET CENTERED. EXECUTING MANEUVER <<<")
            drone.send_rc_control(0, 0, 0, 0) 
            time.sleep(1.0) # Full second to stop any remaining wobble
            
            drone.move_forward(50) 
            time.sleep(1.0)
            drone.move_up(50)      
            
            print(">>> ITEM SECURED <<<")
            maneuver_complete = True
            stable_start_time = None 

        # Apply centering movements (Forward/Backward is always 0)
        if is_flying and not maneuver_complete:
            drone.send_rc_control(lr_speed, 0, ud_speed, 0)

        cv2.imshow("AeroAid Steady Mission", img)
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
    drone.streamoff()
    cv2.destroyAllWindows()