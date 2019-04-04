import threading
import datetime
import _thread
import time

# This class holds objects of the PWM lib etc.
# You can replace the print with all the sets to drive the motors
class MotorController:
    
    def __init__(self):
        self.lastCommandTime = datetime.datetime.now()
        self.receivedNewDriveCommandBool = False
        
    def forwardDrive(self):
        self.receivedNewDriveCommandBool = True
        self.lastCommandTime = datetime.datetime.now()
        print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + " : Setting params of PWM to drive forward (" + str(threading.get_ident()) + ")")
        
    def reverseDrive(self):
        self.receivedNewDriveCommandBool = True
        self.lastCommandTime = datetime.datetime.now()
        print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + " : Setting params of PWM to drive backward (" + str(threading.get_ident()) + ")")
        
    def allStop(self):
        # No set here since it is not a drive command and we are already stopped
        print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + " : Setting params of PWM to stop all motors (" + str(threading.get_ident()) + ")")
        
    def getSecondsSinceLastDriveCommand(self):
        return (datetime.datetime.now() - self.lastCommandTime).total_seconds()
        
    def clearReceivedNewDriveCommandBool(self):
        self.receivedNewDriveCommandBool = False
    
    def getReceivedNewDriveCommandBool(self):
        return self.receivedNewDriveCommandBool
        
        
# Main controller that is thread safe
class MainController:
    
    # Ammount of s of no requests before we stop driving
    safetyStopTime = 2
    
    def __init__(self, motorController, ledController):
        self.motorController = motorController
        self.ledController = ledController
        self.lock = threading.Lock()
        self.enableCheckMotorThreadBool = True
    
    def driveDirection(self, direction):
        self.lock.acquire() # Lock the motorController
        try:
            if(direction == "up"):
                self.motorController.forwardDrive()
            elif(direction == "down"):
                self.motorController.reverseDrive()
            elif(direction == "stop"):
                self.motorController.allStop()
        finally:
            self.lock.release() # Release the lock
    
    # This method continuesly checks if 
    def checkMotorThread(self):
        while(self.enableCheckMotorThreadBool):
            self.lock.acquire()
            try:
                # Has a command been received recently & has this been more then X seconds ago?
                if(self.motorController.getReceivedNewDriveCommandBool() and self.motorController.getSecondsSinceLastDriveCommand() > self.safetyStopTime):
                    print("CheckMotorThread detected no recent commands while still driving, stopping motors")
                    self.motorController.allStop()
                    self.motorController.clearReceivedNewDriveCommandBool()
            finally:
                self.lock.release()
            
            # Poll every 250ms
            time.sleep(.25)
        



# END OF CLASS DECLARATION
# Global properties
motorController = MotorController()
mainController = MainController(motorController, None)
# Enable the check thread that will stop the motors after 1s
_thread.start_new_thread(mainController.checkMotorThread, ())


def HandleRequest(action):
    print("Handling request: " + action)
    mainController.driveDirection(action)
    

# Main function that simulates requests coming in on different threads
def main():
    
    # Create thread that drives forward
    _thread.start_new_thread(HandleRequest, ("up", ))
    time.sleep(1)
    _thread.start_new_thread(HandleRequest, ("down", ))
    
    while 1:
        pass

# Let start out code with main
if __name__ == '__main__':
    main()
