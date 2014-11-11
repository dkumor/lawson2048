#!/usr/bin/python
'''
    Adapted from simple mjpeg stream server (Igor Maculan - n3wtron@gmail.com)

'''

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from lawsoncam import LawsonCamera
import keyboard
import SocketServer
import os
import sys
import mimetypes

sitedir = os.path.dirname(os.path.realpath(__file__))
server = None  # the current executing server so we can do shutdown

class CamHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return
        
    def send_200_type(self, contenttype, length=None):
        self.send_response(200)
        self.send_header('Content-type', contenttype)
        
        if length != None:
            self.send_header('Content-length', length)
        
        self.end_headers()

    def do_GET(self):
        global server
        
        if "?" in self.path:
            self.path = self.path[:self.path.find("?")]

        if self.path in ["", None, "/"]:
            self.path = "/index.html"

        if self.path.endswith('.mjpg'):

            cam = LawsonCamera()
            cam.loadGlob("./assets/keys/*.jpg")
            cam.addCall("up",keyboard.up)
            cam.addCall("down",keyboard.down)
            cam.addCall("left",keyboard.left)
            cam.addCall("right",keyboard.right)

            cam.start("http://128.10.29.32/mjpg/1/video.mjpg")

            self.send_200_type('multipart/x-mixed-replace; boundary=--jpgboundary')

            try:
                while True:
                    jpg = cam.jpgstream()
                    self.wfile.write("--jpgboundary")
                    self.send_200_type('image/jpeg', len(jpg))
                    self.wfile.write(jpg)

                    keyboard.update_pct(cam.keyactivation['up'],cam.keyactivation['down'],cam.keyactivation['left'],cam.keyactivation['right'])

                    
            except:
                #There was some kind of error - clean up the camera
                cam.stop()
            return


        if 'keyboard_event.js' in self.path:
            self.send_200_type('text/javascript')
            self.wfile.write(keyboard.getKeypresses())
            return

        if "shutdown" in self.path:
            self.send_200_type('text/html')
            self.wfile.write("<h1>Shutdown!</h1>")
            server.shutdown()
            return

        mime, tmp = mimetypes.guess_type(self.path)
        if mime == None:
            mime = 'application/octet-stream'

        self.send_200_type(mime)
        try:
            with open(sitedir + self.path) as f:
                self.wfile.write(f.read())
        except:
            pass #ignore it    


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    try:
        port = int(sys.argv[1])
    except:
        port = 8080

    print("Starting on http://localhost:{}".format(port))
    
    try:
        server = ThreadedTCPServer(('', port), CamHandler)
        print "server started"
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()
