#!/usr/bin/env python

import keyboard
import webbrowser
import os
import time
import cvserver
import threading


def startbrowser():
    time.sleep(5)
    path =  "file://" + os.path.abspath("index.html")    
    webbrowser.open(path)
    time.sleep(3)    
    keyboard.fullscreen()

if __name__ == "__main__":

    #t = threading.Thread(target = startbrowser)
    #t.start()
    cvserver.main()
