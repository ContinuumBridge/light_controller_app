#!/usr/bin/env python
# Light Controller App
"""
Copyright (c) 2017 ContinuumBridge Limited
"""

import sys
import json
from cbcommslib import CbApp
from cbconfig import *
import time
from twisted.internet import reactor

ModuleName          = "Light Controller"
CHECK_DELAY         = 60   # How often to check the times and switch
colours             = ["soft_white", "cold_white", "red", "green", "blue"]
ontimes             = []
offtimes            = []
configFile          = CB_CONFIG_DIR + "circadian.json"

class App(CbApp):
    def __init__(self, argv):
        self.appClass = "control"
        self.state = "stopped"
        self.colourIndex = 1
        self.brightnesses = {"soft_white": "0",
            "cold_white": "255",
            "red": "0",
            "green": "0",
            "blue": "0"
        }
        self.brightness = 255
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

    def readTimings(self):
        global ontimes, offtimes
        logging.info("{} Reading times from: {}".format(ModuleName, configFile))
        try:
            with open(configFile, 'r') as f:
                config = json.load(f)
                ontimes = config["ontimes"]
                logging.debug("%s ontimes: %s", ModuleName, ontimes)
                offtimes = config["offtimes"]
                logging.debug("%s offtimes: %s", ModuleName, offtimes)
        except Exception as ex:
            logging.warning('%s circadian.json does not exist or file is corrupt', ModuleName)
            logging.warning("%s Exception: %s %s", ModuleName, type(ex), str(ex.args))

    def doTiming(self):
        if self.gotSwitch:
            now = time.strftime('%a %H:%M', time.localtime())
            for t in ontimes:
                if t == now:
                    for b in self.brightnesses:
                        if b == "cold_white":
                            self.brightnesses[b] = "255"
                        else:
                            self.brightnesses[b] = "0"
                    self.cbLog("debug", "doTiming, sending: {}".format(self.brightnesses))
                    self.sendCommand(self.brightnesses)
            for t in offtimes:
                if t == now:
                    for b in self.brightnesses:
                        if b == "soft_white":
                            self.brightnesses[b] = "150"
                        else:
                            self.brightnesses[b] = "0"
                    self.cbLog("debug", "doTiming, sending: {}".format(self.brightnesses))
                    self.sendCommand(self.brightnesses)
        reactor.callLater(CHECK_DELAY, self.doTiming)

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

    def sendCommand(self, data):
        r = {"id": self.id,
             "request": "command",
             "characteristic": "rgbww",
             "data": data
            }
        self.sendMessage(r, self.switchID)

    def onAdaptorService(self, message):
        self.cbLog("debug", "onAdaptorService, message: " + str(json.dumps(message, indent=4)))
        controller = None
        switch = False
        for s in message["service"]:
            if s["characteristic"] == "number_buttons": 
                controller = s["characteristic"]
            elif s["characteristic"] == "led_rgbww":
                self.switchID = message["id"]
                switch = True
                self.gotSwitch = True
        if controller and not switch:
            self.sensorsID.append(message["id"])
            self.sendServiceResponse(controller, message["id"])
        self.setState("running")

    def onAdaptorData(self, message):
        #self.cbLog("debug", "onAdaptorData, message: " + str(json.dumps(message, indent=4)))
        if message["id"] in self.sensorsID:
            if self.gotSwitch:
                if message["characteristic"] == "number_buttons":
                    data = message["data"]
                    change = False
                    if "1" in data:
                        self.brightness += 50
                        if self.brightness > 249:
                            self.brightness = 255
                        change = True
                    elif "3" in data:
                        self.brightness -= 50
                        if self.brightness < 5:
                            self.brightness = 0
                        change = True
                    if "2" in data:
                        self.colourIndex = (self.colourIndex + 1)%5
                        change = True
                    elif "4" in data:
                        if self.colourIndex == 0:
                            self.colourIndex = 4
                        else:
                            self.colourIndex = self.colourIndex - 1
                        change = True
                    if change:
                        for b in self.brightnesses:
                            if b == colours[self.colourIndex]:
                                self.brightnesses[b] = str(self.brightness)
                            else:
                                self.brightnesses[b] = "0"
                        self.cbLog("debug", "onAdaptorData, sending: {}".format(self.brightnesses))
                        self.sendCommand(self.brightnesses)
            else:
                self.cbLog("debug", "Trying to turn on/off before switch connected")

    def onConfigureMessage(self, config):
        self.readTimings()
        self.doTiming()
        self.setState("starting")

if __name__ == '__main__':
    App(sys.argv)
