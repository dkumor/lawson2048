#!/usr/bin/python
'''
    Adapted from simple mjpeg stream server (Igor Maculan - n3wtron@gmail.com)

'''

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from lawsoncam import LawsonCamera
import urllib
import numpy as np
import time
import keyboard
import SocketServer
import os
from threading import Thread
import logging

sitedir = os.path.dirname(os.path.realpath(__file__))

averageover = 100

#Bigger number means slower
speed = 3000000.0
equalizer= 1200.0
rect = {
    "up": [(170,0+15),(170*2,128+15),0,zeros(averageover)],
    "down": [(170,128*2),(170*2,128*3),0,zeros(averageover)],
    "left": [(0,128),(170,128*2),0,zeros(averageover)],
    "right": [(170*2,128),(170*3,128*2),0,zeros(averageover)],
}

class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global rect
        global speed
        if self.path.endswith('.mjpg'):
            
            cam = LawsonCamera()

            reset = False
            self.send_response(200)
            self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()

            while True:
                try:

                    jpg = cam.jpgstream()
                    self.wfile.write("--jpgboundary")
                    self.send_header('Content-type','image/jpeg')
                    self.send_header('Content-length',len(jpg))
                    self.end_headers()
                    self.wfile.write(jpg)

                except KeyboardInterrupt:
                    break
            return


        if 'keyboard_event.js' in self.path:
          self.send_response(200)
          self.send_header('Content-type', 'text/javascript')
          self.end_headers()
          self.wfile.write(keyboard.getKeypresses())
          return


        pathmap = {'.html':'text/html', '.js':'text/javascript', '.css':'text/css'}
        mime = 'application/octet-stream'

        for k, v  in pathmap.items():
            if self.path.endswith(k):
                mime = v

        self.send_response(200)
        self.send_header('Content-type', mime)
        self.end_headers()
        try:
            f = open(sitedir + self.path)
            self.wfile.write(f.read())
            f.close()
        except IOError, e: # probably means we tried fetching a directory
            self.wfile.write("Couldn't find file")
            print e


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

def main():
    try:
        server = ThreadedTCPServer(('',8080), CamHandler)
        print "server started"
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()
