import requests
import threading
import time
import os    # Added
import cv2   # Added
from flask import Flask, render_template, request, jsonify
from djitellopy import Tello

app = Flask(__name__)

# --- HELPER FUNCTION: FIREBASE STATUS ---
def set_status(order_id, new_status):
    """Updates the status in Firebase via Ethernet Internet"""
    if order_id:
        url = f"https://aeroaid-93195-default-rtdb.asia-southeast1.firebasedatabase.app/orders/{order_id}.json"
        try:
            requests.patch(url, json={"status": new_status})
        except Exception as e:
            print(f"Firebase Update Error: {e}")

# --- REAL DRONE MISSION FUNCTION ---
def run_drone_mission(location, order_id):
    # Initialize the real Tello
    drone = Tello()
    
    try:
        print(f"Attempting to connect to Tello for order: {order_id}...")
        set_status(order_id, "CONNECTING TO DRONE...")
        
        # Connect via Wi-Fi (Does not use Port 9999)
        drone.connect()
        
        # Turn on the camera of the drone
        drone.streamon()

        # Safety Check: Battery
        battery = drone.get_battery()
        print(f"Battery Life: {battery}%")
        if battery < 20:
            set_status(order_id, f"ABORTED: LOW BATTERY ({battery}%)")
            return

        # Start Flight Sequence
        set_status(order_id, "TAKEOFF...")
        drone.takeoff()
        time.sleep(1)

        set_status(order_id, f"EN ROUTE TO {location.upper()}")
        
        # Movement Logic (Tello uses centimeters: 100cm = 1m)
        if location == "Block A1":
            drone.move_forward(100)
            drone.move_left(100)
        elif location == "Block B2":
            drone.move_forward(100)
            drone.move_right(100)
        elif location == "Dewan Kuliah":
            drone.move_forward(100)
        elif location == "Kafeteria":
            drone.move_right(100)
        elif location == "Langkasuka":
            drone.move_back(100)
        elif location == "Perpustakaan":
            drone.move_left(100)
        else: 
            drone.move_back(100)
            drone.move_right(100)
        
        # --- IMPROVED PHOTO LOGIC ---
        set_status(order_id, "TAKING PHOTO...")
        
        # 1. Get the background frame reader
        frame_read = drone.get_frame_read()
        
        # 2. Give the buffer a moment to clear old/empty frames
        time.sleep(2) 
        
        # 3. Grab the latest frame
        frame = frame_read.frame
        
        if frame is not None:
            # Tello frames are often in RGB, OpenCV needs BGR to save correctly
            # If the colors look weird later, you can add: 
            # frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            photo_name = f"delivery_{order_id}.jpg"
            photo_path = os.path.join('static', 'image', photo_name)
            
            # Save the image
            cv2.imwrite(photo_path, frame)
            
            # Update Firebase
            url = f"https://aeroaid-93195-default-rtdb.asia-southeast1.firebasedatabase.app/orders/{order_id}.json"
            requests.patch(url, json={"delivery_photo": f"/static/image/{photo_name}"})
            print(f"Photo successfully saved: {photo_path}")

        # End Flight Sequence
        set_status(order_id, "DRONE REACHED!")
        drone.land()

    except Exception as e:
        # THE SAFETY NET: Catches issues if Wi-Fi drops or drone isn't found
        error_msg = str(e)
        print(f"CRITICAL DRONE ERROR: {error_msg}")
        set_status(order_id, f"SIGNAL ERROR: {error_msg[:20]}")

    finally:
        # Gracefully close the connection to the drone
        try:
            drone.streamoff() # Add this to save battery/bandwidth
            drone.end()
        except:
            pass

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/order')
def order_page():
    return render_template('order.html')

@app.route('/dispatch', methods=['POST'])
def dispatch():
    data = request.get_json()
    location = data.get('location')
    order_id = data.get('orderId')

    # Run in background so the UI doesn't hang
    thread = threading.Thread(target=run_drone_mission, args=(location, order_id))
    thread.start()

    return jsonify({"success": True, "message": "Real drone dispatched!"})

if __name__ == "__main__":
    app.run(port=5000, debug=True)