# Copyright (c) 2013 phrack. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import random
import threading
from threading import Thread
import time
from training_protocols.ITrainingProtocol import ITrainingProtocol 

class TimedHolsterDrill(ITrainingProtocol):
    def __init__(self, main_window, protocol_operations, targets):
        self._operations = protocol_operations

        self._operations.add_shot_list_columns(("Length",), [60])
        self._operations.pause_shot_detection(True)    

        self._repeat_protocol = True
        self._parent = main_window
        self._operations.get_delayed_start_interval(self._parent, self.update_interval)

        self._wait_event = threading.Event()

        self._setup_wait = Thread(target=self.setup_wait,
                                          name="setup_wait_thread")
        self._setup_wait.start()

    def update_interval(self, new_min, new_max):
        self._interval_min = new_min
        self._interval_max = new_max

    def setup_wait(self):
        # Give the shooter 10 seconds to position themselves
        self._wait_event.wait(10)
        self._operations.say("Preparados, Shooter... make ready")

        if self._repeat_protocol:
            self._random_delay = Thread(target=self.random_delay,
                                          name="random_delay_thread")
            self._random_delay.start()

    def random_delay(self):
        random_delay = random.randrange(self._interval_min, self._interval_max)
        self._wait_event.wait(random_delay)

        if self._repeat_protocol:
            self._operations.play_sound("sounds/beep.wav")
            self._operations.pause_shot_detection(False)
            self._beep_time = time.time()
            self.random_delay()

    def shot_listener(self, shot, shot_list_item, is_hit):
        # Calculate difference between beep time and current time and
        # add it to the list
        draw_shot_length = time.time() - self._beep_time
        self._operations.append_shot_item_values(shot_list_item, (draw_shot_length,))

    def hit_listener(self, region, tags, shot, shot_list_item):
        pass

    def reset(self, targets):        
        self._repeat_protocol = False
        self._wait_event.set()
        self._operations.get_delayed_start_interval(self._parent, self.update_interval)
        self._repeat_protocol = True
        self._wait_event.clear()

        self._random_delay = Thread(target=self.random_delay,
                                          name="random_delay_thread")
        self._random_delay.start()

    def destroy(self):
        self._repeat_protocol = False
        self._wait_event.set()

def get_info():
    protocol_info = {}

    protocol_info["name"] = "Timed Holster Drill"
    protocol_info["version"] = "1.0"
    protocol_info["creator"] = "phrack"
    desc = "This protocol does not require a target, but one may be used " 
    desc += "to give the shooter something to shoot at. When the protocol "
    desc += "is started you are asked to enter a range for randomly "
    desc += "delayed starts. You are then given 10 seconds to position "
    desc += "yourself. After a random wait (within the entered range) a "
    desc += "beep tells you to draw their pistol from it's holster, "
    desc += "fire at your target, and finally re-holster. This process is "
    desc += "repeated as long as this protocol is on."
    protocol_info["description"] = desc

    return protocol_info

def load(main_window, protocol_operations, targets):
    return TimedHolsterDrill(main_window, protocol_operations, targets)
