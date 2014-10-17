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


class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global rect
        global speed
        if self.path.endswith('.mjpg'):
            
            cam = LawsonCamera("http://128.10.29.32/mjpg/1/video.mjpg")
            #cam = LawsonCamera()

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

def main(port):
    try:
        server = ThreadedTCPServer(('',port), CamHandler)
        print "server started"
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()
