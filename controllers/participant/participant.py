# Copyright 1996-2023 Cyberbotics Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Minimalist controller example for the Robot Wrestling Tournament.
   Demonstrates how to play a simple motion file."""
from controller import Robot
import sys

# We provide a set of utilities to help you with the development of your controller. You can find them in the utils folder.
# If you want to see a list of examples that use them, you can go to https://github.com/cyberbotics/wrestling#demo-robot-controllers
sys.path.append('..')
from utils.motion_library import MotionLibrary
from utils.accelerometer import Accelerometer

class Dumul (Robot):
    def __init__(self):
        super().__init__()
        self.time_step = int(self.getBasicTimeStep())
        self.library = MotionLibrary()
        self.accelerometer = Accelerometer(self, self.time_step)
        self.RShoulderRoll = self.getDevice("RShoulderRoll")
        self.LShoulderRoll = self.getDevice("LShoulderRoll")
      
    def detect_fall(self):
        [acc_x, acc_y, _] = self.accelerometer.get_new_average()
        if acc_x < -7:
            self.library.play('GetUpFront')
        elif acc_x > 7:
            self.library.play('GetUpBack')
        if acc_y < -7:
            # Fell to its right, pushing itself on its back
            self.RShoulderRoll.setPosition(-1.2)
        elif acc_y > 7:
            # Fell to its left, pushing itself on its back
            self.LShoulderRoll.setPosition(1.2)
         
    def run(self):
        while self.step(self.time_step) != -1:  # mandatory function to make the simulation run
            self.detect_fall()
            if self.getTime() >= 1 and self.getTime() < 45:
               self.library.play('SideStepLeft')
            if self.getTime() >= 45 and self.getTime() < 95:
               self.library.play('Forwards')
            if self.getTime() >= 95 and self.getTime() < 195:
               self.library.play('SideStepRight')    
            


# create the Robot instance and run main loop
wrestler = Dumul()
wrestler.run()
