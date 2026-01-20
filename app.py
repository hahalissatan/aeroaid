import requests
import threading
from DroneBlocksTelloSimulator.DroneBlocksSimulatorContextManager import DroneBlocksSimulatorContextManager
from flask import Flask, render_template, request

app = Flask(__name__)

SIM_KEY = 'd10e4fb0-595f-46f6-9b76-571356bc4ef3' 

# 1. THE HOME PAGE
@app.route('/')
def index():
    return render_template('index.html')

# 2. THE MENU PAGE
@app.route('/menu')
def menu():
    return render_template('menu.html')

# 3. THE HISTORY PAGE
@app.route('/history')
def history():
    return render_template('history.html')

# 5. THE ORDER CONFIRMATION PAGE
@app.route('/order')
def order_page():
    return render_template('order.html')

# --- NEW MISSION FUNCTION ---
# This function handles the drone flight in a background thread
def run_drone_mission(location, order_id):
    # Helper function to update the status text in Firebase
    def set_status(new_status):
        if order_id:
            url = f"https://aeroaid-93195-default-rtdb.asia-southeast1.firebasedatabase.app/orders/{order_id}.json"
            try:
                requests.patch(url, json={"status": new_status})
            except Exception as e:
                print(f"Firebase Update Error: {e}")

    # Run the DroneBlocks Code
    with DroneBlocksSimulatorContextManager(simulator_key=SIM_KEY) as drone:
        # --- PHASE 1 ---
        set_status("Processing to takeoff...")
        drone.takeoff()

        # --- PHASE 2 ---
        set_status(f"Delivering to {location}...")
        
        # Logic based on the 'H' marks on the pad
        if location == "Block A1":
            drone.fly_forward(100, 'cm')
            drone.fly_left(100, 'cm')
        elif location == "Block B2":
            drone.fly_forward(100, 'cm')
            drone.fly_right(100, 'cm')
        elif location == "Dewan Kuliah":
            drone.fly_forward(100, 'cm')
        elif location == "Kafeteria":
            drone.fly_right(100, 'cm')
        elif location == "Langkasuka":
            drone.fly_backward(100, 'cm')
        elif location == "Perpustakaan":
            drone.fly_left(100, 'cm')
        else: 
            drone.fly_backward(100,'cm')
            drone.fly_right(100, 'cm')
        
        # Land the drone
        drone.land()
        set_status("DRONE REACHED!")

# --- UPDATED DISPATCH ROUTE ---
@app.route('/dispatch', methods=['POST'])
def dispatch():
    # Get the data sent from the JavaScript
    data = request.get_json()
    location = data.get('location')
    order_id = data.get('orderId') # Make sure this matches your JavaScript key

    # Start the drone mission in a separate thread so the website doesn't wait
    thread = threading.Thread(target=run_drone_mission, args=(location, order_id))
    thread.start()

    return "Dispatched!"

if __name__ == "__main__":
    app.run(port=5000, debug=True)