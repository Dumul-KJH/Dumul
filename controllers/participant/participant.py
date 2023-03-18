import sys
from controller import Robot
sys.path.append('..')
from utils.accelerometer import Accelerometer
from utils.finite_state_machine import FiniteStateMachine
from utils.motion_library import MotionLibrary
from utils.current_motion_manager import CurrentMotionManager

class Dumul (Robot):
    def __init__(self):
        super().__init__()
        self.time_step = int(self.getBasicTimeStep())
        self.fsm = FiniteStateMachine(
            states=['BLOCKING_MOTION', 'FRONT_FALL', 'BACK_FALL','FRONT_WALK', 'LEFT_WALK', 'RIGHT_WALK'],
            initial_state='BLOCKING_MOTION',
            actions={
                'BLOCKING_MOTION': self.pending,
                'FRONT_WALK': self.walk,
                'LEFT_WALK' : self.left,
                'RIGHT_WALK' : self.right,
                'FRONT_FALL': self.front_fall,
                'BACK_FALL': self.back_fall
            }
        )
        
        self.accelerometer = Accelerometer(self, self.time_step)
        self.leds = {
            'right': self.getDevice('Face/Led/Right'),
            'left': self.getDevice('Face/Led/Left')
        }
        self.RShoulderRoll = self.getDevice("RShoulderRoll")
        self.LShoulderRoll = self.getDevice("LShoulderRoll")
        self.current_motion = CurrentMotionManager()
        self.library = MotionLibrary()
      
    def detect_fall(self):
        '''Detect a fall and update the FSM state.'''
        [acc_x, acc_y, _] = self.accelerometer.get_new_average()
        if acc_x < -7:
            self.fsm.transition_to('FRONT_FALL')
        elif acc_x > 7:
            self.fsm.transition_to('BACK_FALL')
        if acc_y < -7:
            # Fell to its right, pushing itself on its back
            self.RShoulderRoll.setPosition(-1.2)
        elif acc_y > 7:
            # Fell to its left, pushing itself on its back
            self.LShoulderRoll.setPosition(1.2)
            
    def pending(self):
        # waits for the current motion to finish before doing anything else
        if self.current_motion.is_over():
            self.fsm.transition_to('BLOCKING_MOTION')

    def walk(self):
        if self.current_motion.get() != self.library.get('ForwardLoop'):
            self.current_motion.set(self.library.get('ForwardLoop'))

    def front_fall(self):
        self.current_motion.set(self.library.get('GetUpFront'))
        self.fsm.transition_to('BLOCKING_MOTION')

    def back_fall(self):
        self.current_motion.set(self.library.get('GetUpBack'))
        self.fsm.transition_to('BLOCKING_MOTION')
     
    def left(self):
        self.current_motion.set(self.library.get('SideStepLeft'))
        self.fsm.transition_to('BLOCKING_MOTION')
        
    def right(self):
        self.current_motion.set(self.library.get('SideStepRight'))
        self.fsm.transition_to('BLOCKING_MOTION')

    def run(self):
        self.leds['right'].set(0x0000ff)
        self.leds['left'].set(0x0000ff)
        self.current_motion.set(self.library.get('Stand'))
        self.fsm.transition_to('BLOCKING_MOTION')
        while self.step(self.time_step) != -1:  # mandatory function to make the simulation run
            self.detect_fall()
            self.fsm.execute_action()
            if self.getTime() >= 1 and self.getTime() < 45:
               self.fsm.transition_to('LEFT_WALK')
            if self.getTime() >= 45 and self.getTime() < 95:
               self.fsm.transition_to('FRONT_WALK')
            if self.getTime() >= 95 and self.getTime() < 195:
               self.fsm.transition_to('RIGHT_WALK')    
            


# create the Robot instance and run main loop
wrestler = Dumul()
wrestler.run()
