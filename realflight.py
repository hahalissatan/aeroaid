from djitellopy import Tello
import time

# Initialize the drone
tello = Tello()

try:
    # Connect to the drone
    tello.connect()
    
    # Check battery first - very important for AeroAid!
    print(f"Battery Life: {tello.get_battery()}%")
    
    # Takeoff
    print("Taking off...")
    tello.takeoff()
    
    # Hover for 3 seconds to test stability
    time.sleep(3)
    
    # Land
    print("Landing...")
    tello.land()

except Exception as e:
    print(f"Error: {e}")