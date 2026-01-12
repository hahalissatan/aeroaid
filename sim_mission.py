import time
from DroneBlocksTelloSimulator.DroneBlocksSimulatorContextManager import DroneBlocksSimulatorContextManager

if __name__ == '__main__':
    sim_key = '7e3fc7bc-203e-47af-989e-84c321712653' 
    
    try:
        with DroneBlocksSimulatorContextManager(simulator_key=sim_key) as drone:
            # Replaced emojis with text to avoid GBK encoding errors
            print("--- Connecting to Virtual Drone ---")
            drone.takeoff()
            time.sleep(2) 
            
            print("--- Flying forward ---")
            drone.fly_forward(100, 'cm')
            time.sleep(2)
            
            print("--- Landing ---")
            drone.land()
            
        print("Done: Mission Complete!")
        input("Press Enter to close this window...") 
        
    except Exception as e:
        # Replaced the red X emoji with "ERROR"
        print(f"ERROR: Connection failed. Details: {e}")
        input("Press Enter to exit...")