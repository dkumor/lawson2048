#!/usr/bin/python
'''
    Adapted from simple mjpeg stream server (Igor Maculan - n3wtron@gmail.com)

'''
import cv2
from PIL import Image
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
import StringIO
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
            stream=urllib.urlopen('http://128.10.29.32/mjpg/1/video.mjpg')
            bytes=''
            print "Videostream open"
            i = None
            i_prev = None

            reset = False
            self.send_response(200)
            self.send_header('Content-type','multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()

            while True:
                try:

                    #HERE IS MONSTER CODE
                    bytes+=stream.read(1024)
                    a = bytes.find('\xff\xd8')
                    b = bytes.find('\xff\xd9')
                    if a!=-1 and b!=-1:

                        jpg = bytes[a:b+2]
                        bytes= bytes[b+2:]
                        if (i_prev==None):
                            #i = cv2.cvtColor(cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR), cv2.COLOR_RGB2GRAY)
                            i =cv2.cvtColor(cv2.resize(cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR),(0,0),fx=0.5,fy=0.5), cv2.COLOR_RGB2GRAY)
                            i = cv2.flip(i,1)
                            i_prev = i
                        else:
                            i_prev = i
                            #i = cv2.cvtColor(cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR), cv2.COLOR_RGB2GRAY)
                            i =cv2.cvtColor(cv2.resize(cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR),(0,0),fx=0.5,fy=0.5), cv2.COLOR_RGB2GRAY)
                            i=cv2.flip(i,1)
                        #size:384,512
                        #Grid: 128 down 170 across
                        d = cv2.absdiff(i,i_prev)

                        pk = None
                        for k in rect:
                            p = rect[k]
                            
                            diff = d[p[0][1]:p[1][1],p[0][0]:p[1][0]].sum()
                            p[2]+= d[p[0][1]:p[1][1],p[0][0]:p[1][0]].sum()/(speed+equalizer*p[3])
                            if (p[2] > 1.0):
                                p[2]= 1.0
                                if k == "up":
                                    keyboard.up()
                                elif k == "down":
                                    keyboard.down()
                                elif k == "left":
                                    keyboard.left()
                                elif k == "right":
                                    keyboard.right()
                                for z in rect:
                                    if (z!=k):
                                        rect[z][3]-=1
                                        if (rect[z][3]<=0):
                                            rect[z][3] = 0
                                p[3]+=3
                                logging.warning(str(k)+" "+str(p[3]))
                                reset = True
                                break

                            cv2.rectangle(i,p[0],p[1],int(255*p[2]),3)
                        if (reset):
                            reset= False
                            minval = rect["up"][3]
                            for k in rect:
                                rect[k][2] = 0.0
                                if (rect[k][3] < minval):
                                    minval = rect[k][3]
                            for k in rect:
                                rect[k][3] -= minval

                        jpg = Image.fromarray(cv2.cvtColor(i,cv2.COLOR_GRAY2RGB))
                        tmpFile = StringIO.StringIO()
                        jpg.save(tmpFile,'JPEG')
                        self.wfile.write("--jpgboundary")
                        self.send_header('Content-type','image/jpeg')
                        self.send_header('Content-length',str(tmpFile.len))
                        self.end_headers()
                        jpg.save(self.wfile,'JPEG')

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
