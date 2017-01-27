#!/usr/bin/env python
# Light Controller App
"""
Copyright (c) 2017 ContinuumBridge Limited
"""

import sys
import json
from cbcommslib import CbApp
from cbconfig import *

class App(CbApp):
    def __init__(self, argv):
        self.appClass = "control"
        self.state = "stopped"
        self.switchState = "0"
        self.gotSwitch = False
        self.sensorsID = [] 
        self.switchID = ""
        # Super-class init must be called
        CbApp.__init__(self, argv)

    def setState(self, action):
        self.state = action
        msg = {"id": self.id,
               "status": "state",
               "state": self.state}
        self.sendManagerMessage(msg)

    def sendServiceResponse(self, characteristic, device):
        r = {"id": self.id,
             "request": "service",
             "service": [
                          {"characteristic": characteristic,
                           "interval": 0
                          }
                        ]
            }
        self.sendMessage(r, device)

    def sendCommand(self, state):
        r = {"id": self.id,
             "request": "command",
             "data": state
            }
        self.sendMessage(r, self.switchID)

    def onAdaptorService(self, message):
        self.cbLog("debug", "onAdaptorService, message: " + str(json.dumps(message, indent=4)))
        controller = None
        switch = False
        for s in message["service"]:
            if s["characteristic"] == "number_buttons": 
                controller = s["characteristic"]
            elif s["characteristic"] == "rgbww":
                self.switchID = message["id"]
                switch = True
                self.gotSwitch = True
        if controller and not switch:
            self.sensorsID.append(message["id"])
            self.sendServiceResponse(controller, message["id"])
        self.setState("running")

    def onAdaptorData(self, message):
        self.cbLog("debug", "onAdaptorData, message: " + str(json.dumps(message, indent=4)))
        if message["id"] in self.sensorsID:
            if self.gotSwitch:
                if message["characteristic"] == "number_buttons":
                    if "1" in data:
                        pass
                    elif "3" in data:
                        pass
                    elif "2" in data:
                        pass
                    elif "4" in data:
                        pass
                if self.switchState == "0":
                    self.switchState = "255"
                else:
                    self.switchState = "0"
                self.sendCommand(self.switchState)
            else:
                self.cbLog("debug", "Trying to turn on/off before switch connected")

    def onConfigureMessage(self, config):
        self.setState("starting")

if __name__ == '__main__':
    App(sys.argv)
