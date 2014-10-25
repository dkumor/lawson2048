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
import sys

sitedir = os.path.dirname(os.path.realpath(__file__))

server = None  # the current executing server so we can do shutdown

class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global rect
        global speed
        global shutdown

        if self.path in ["", None, "/"]:
            self.path = "/index.html"

        if self.path.endswith('.mjpg'):

            cam = LawsonCamera()
            cam.loadGlob("./assets/keys/*.jpg")

            cam.addCall("up",keyboard.up())
            cam.addCall("down",keyboard.down())
            cam.addCall("left",keyboard.left())
            cam.addCall("right",keyboard.right())

            cam.start("http://128.10.29.32/mjpg/1/video.mjpg")
            #cam.start()

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

        if "shutdown" in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("<h1>Shutdown!</h1>")
            server.shutdown()
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
    global server

    if server != None:
        server.shutdown()
    try:
        server = ThreadedTCPServer(('',port), CamHandler)
        print "server started"
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()


if __name__ == "__main__":
    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    print("Starting on http://localhost:{}".format(port))
    main(port)
