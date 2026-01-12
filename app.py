from DroneBlocksTelloSimulator.DroneBlocksSimulatorContextManager import DroneBlocksSimulatorContextManager
from flask import Flask, render_template

app = Flask(__name__) # Keep __name__ exactly like this

# This is where you paste the key from the website
SIM_KEY = 'fe32be9d-238f-4478-bae0-cb008b2f320c' 

# --- MISSING PIECE ADDED BELOW ---
@app.route('/')
def index():
    # This tells Flask to look for 'index.html' inside your 'templates' folder
    return render_template('index.html')
# ---------------------------------

@app.route('/dispatch', methods=['POST'])
def dispatch():
    # This 'with' block manages the connection to the simulator
    with DroneBlocksSimulatorContextManager(simulator_key=SIM_KEY) as drone:
        drone.takeoff()
        drone.fly_forward(40, 'in')
        drone.land()
    return "Dispatched!"

if __name__ == "__main__": # Keep __name__ exactly like this
    app.run(port=5000, debug=True)