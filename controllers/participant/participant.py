import sys
from controller import Robot
sys.path.append('..')
from utils.fall_detection import FallDetection
from utils.accelerometer import Accelerometer
from utils.finite_state_machine import FiniteStateMachine
from utils.motion_library import MotionLibrary
from utils.current_motion_manager import CurrentMotionManager

# Image Processing
from utils.camera import Camera
from utils.running_average import RunningAverage
from utils.image_processing import ImageProcessing as IP
import cv2

class Dumul (Robot):
    NUMBER_OF_DODGE_STEPS = 10
    def __init__(self):
        super().__init__()
        self.time_step = int(self.getBasicTimeStep())
        self.fsm = FiniteStateMachine(
            states=['BLOCKING_MOTION' ,'FRONT_WALK', 'LEFT_WALK', 'RIGHT_WALK', 'TURN_RIGHT'],
            initial_state='BLOCKING_MOTION',
            actions={
                'BLOCKING_MOTION': self.pending,
                'FRONT_WALK': self.walk,
                'LEFT_WALK' : self.left,
                'RIGHT_WALK' : self.right,
                'TURN_RIGHT' : self.turn,
            }
        )
        self.fall_detector = FallDetection(self.time_step, self)
        self.accelerometer = Accelerometer(self, self.time_step)
        self.leds = {
            'right': self.getDevice('Face/Led/Right'),
            'left': self.getDevice('Face/Led/Left')
        }
        self.RShoulderRoll = self.getDevice("RShoulderRoll")
        self.LShoulderRoll = self.getDevice("LShoulderRoll")
        self.current_motion = CurrentMotionManager()
        self.library = MotionLibrary()
        
        #image processing
        self.camera = Camera(self)
        self.opponent_position = RunningAverage(dimensions=1)
        self.dodging_direction = 'left'
        self.counter = 0

    def run(self):
        self.leds['right'].set(0x0000ff)
        self.leds['left'].set(0x0000ff)
        self.current_motion.set(self.library.get('Stand'))
        self.fsm.transition_to('BLOCKING_MOTION')
        check = 0
        while self.step(self.time_step) != -1:  # mandatory function to make the simulation run
            self.fall_detector.check()
            self.fsm.execute_action()
            if self.getTime() < 55:
               self.fsm.transition_to('LEFT_WALK')
            elif check == 0:
                self.fsm.transition_to('TURN_RIGHT')
                check = 1
            elif self.current_motion.is_over() and check == 1:
                self.fsm.transition_to('TURN_RIGHT')
                check = 2
            elif self.current_motion.is_over() and self.getTime() < 77 and check == 2:
                self.fsm.transition_to('FRONT_WALK')
                check = 3
            else:
                self.fsm.transition_to('BLOCKING_MOTION')
            
            
    def pending(self):
        # waits for the current motion to finish before doing anything else
        if self.current_motion.is_over():
            self.fsm.transition_to('BLOCKING_MOTION')

    def walk(self):
        if self.current_motion.get() != self.library.get('ForwardLoop'):
            self.current_motion.set(self.library.get('ForwardLoop'))
     
    def left(self):
        self.current_motion.set(self.library.get('SideStepLeft'))
        self.fsm.transition_to('BLOCKING_MOTION')
        
    def right(self):
        self.current_motion.set(self.library.get('SideStepRight'))
        self.fsm.transition_to('BLOCKING_MOTION')
    
    def turn(self):
        self.current_motion.set(self.library.get('TurnRight20'))
        self.fsm.transition_to('BLOCKING_MOTION')
 
    def _get_normalized_opponent_horizontal_position(self):
        """Returns the horizontal position of the opponent in the image, normalized to [-1, 1]
            and sends an annotated image to the robot window."""
        img = self.camera.get_image()
        largest_contour, vertical, horizontal = self.locate_opponent(img)
        output = img.copy()
        if largest_contour is not None:
            cv2.drawContours(output, [largest_contour], 0, (255, 255, 0), 1)
            output = cv2.circle(output, (horizontal, vertical), radius=2,
                                color=(0, 0, 255), thickness=-1)
        self.camera.send_to_robot_window(output)
        if horizontal is None:
            return 0
        return horizontal * 2 / img.shape[1] - 1

    def locate_opponent(self, img):
        """Image processing demonstration to locate the opponent robot in an image."""
        # we suppose the robot to be located at a concentration of multiple color changes (big Laplacian values)
        laplacian = cv2.Laplacian(img, cv2.CV_8U, ksize=3)
        # those spikes are then smoothed out using a Gaussian blur to get blurry blobs
        blur = cv2.GaussianBlur(laplacian, (0, 0), 2)
        # we apply a threshold to get a binary image of potential robot locations
        gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY)
        # the binary image is then dilated to merge small groups of blobs together
        closing = cv2.morphologyEx(
            thresh, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15)))
        # the robot is assumed to be the largest contour
        largest_contour = IP.get_largest_contour(closing)
        if largest_contour is not None:
            # we get its centroid for an approximate opponent location
            vertical_coordinate, horizontal_coordinate = IP.get_contour_centroid(
                largest_contour)
            return largest_contour, vertical_coordinate, horizontal_coordinate
        else:
            # if no contour is found, we return None
            return None, None, None    
            


# create the Robot instance and run main loop
wrestler = Dumul()
wrestler.run()
