from DroneBlocksTelloSimulator.DroneBlocksSimulatorContextManager import DroneBlocksSimulatorContextManager
from flask import Flask, render_template, request

app = Flask(__name__)

SIM_KEY = '8d510f6d-e1e4-440e-a957-fb58d0683fa2' 

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

@app.route('/dispatch', methods=['POST'])
def dispatch():
    # Get the data sent from the JavaScript
    data = request.get_json()
    location = data.get('location')

    # Run the DroneBlocks Code
    with DroneBlocksSimulatorContextManager(simulator_key=SIM_KEY) as drone:
        drone.takeoff()
        
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

    return "Dispatched!"

if __name__ == "__main__":
    app.run(port=5000, debug=True)