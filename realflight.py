from djitellopy import Tello
import time

# Initialize the drone
tello = Tello()

# Connect to the drone
tello.connect()

# Check battery level before flight (Safety first!)
print(f"Battery life: {tello.get_battery()}%")

# Start flight sequence
tello.takeoff()

# Move forward (Distance is in centimeters, min 20, max 500)
tello.move_forward(50)

# Wait for 1 second to stabilize
time.sleep(1)

# Land the drone
tello.land()