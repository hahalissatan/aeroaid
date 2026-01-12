from DroneBlocksTelloSimulator.DroneBlocksSimulatorContextManager import DroneBlocksSimulatorContextManager
from flask import Flask, render_template, request

app = Flask(__name__)

SIM_KEY = 'fe32be9d-238f-4478-bae0-cb008b2f320c' 

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
    matric = data.get('matric')
    location = data.get('location')
    item = data.get('item')

    # 1. Send the Telegram message to HEP
    send_hep_alert(matric, location, item)

    # 2. Run the DroneBlocks Code
    with DroneBlocksSimulatorContextManager(simulator_key=SIM_KEY) as drone:
        drone.takeoff()
        drone.fly_forward(40, 'in')
        drone.land()
        
    return "Dispatched!"

if __name__ == "__main__":
    app.run(port=5000, debug=True)