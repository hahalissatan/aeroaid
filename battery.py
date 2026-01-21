from djitellopy import Tello
import time

# Initialize the drone
tello = Tello()

# Connect to the drone
tello.connect()

# Check battery level before flight (Safety first!)
print(f"Battery life: {tello.get_battery()}%")
