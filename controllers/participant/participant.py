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


class Dumul (Robot):
    def __init__(self):
        super().__init__()
        self.library = MotionLibrary()
        #self.RShoulderPitch = self.getDevice("RShoulderPitch")
        #self.LShoulderPitch = self.getDevice("LShoulderPitch")
         
    def run(self):
        
        time_step = int(self.getBasicTimeStep())
        while self.step(time_step) != -1:  # mandatory function to make the simulation run
            if self.getTime() >= 1 and self.getTime() < 40:
               self.library.play('SideStepLeft')
            if self.getTime() == 41:
               self.library.play('Forwards50')
               self.library.play('Forwards50')
               self.library.play('Forwards50')
               self.library.play('Forwards50')
            if self.getTime() >= 60 and self.getTime() < 100:
               self.library.play('SideStepRight')    
            


# create the Robot instance and run main loop
wrestler = Dumul()
wrestler.run()
