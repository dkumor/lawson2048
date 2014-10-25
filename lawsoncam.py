import numpy as np
from numpy.random import uniform

import cv2
from PIL import Image

from cStringIO import StringIO
import glob
import os

class LawsonCamera(object):
    """Allows key control based on Lawson's webcam"""
    #calcsize = (512,372)
    calcsize = (1024,744)
    ndelta = 0.01
    norm = 0.0
    multiplier = 1.0
    def __init__(self):
        self.keys = {}
        self.keyfnc = {}
    def start(self,address="rtsp://128.10.29.32:554/axis-media/media.amp?videocodec=h264&amp;camera=1&amp;streamprofile=Bandwidth"):
        self.cap = cv2.VideoCapture(address)

        #Get a frame
        self.oldframe = self.resizeToCalc(self.getFrame())

        #Initialize key normalizers
        self.keynorm = {}
        self.keyactivation = {}
        for k in self.keys:
            self.keynorm[k] = self.norm
            self.keyactivation[k] = 0.0



    def getFrame(self):
        ret, frame = self.cap.read()
        return frame

    def getLawsonFrame(self):
        #Lawson's cameras have a black strip above video feed - remove the strip
        return self.getFrame()[24:]


    def __call__(self):
        frame = self.getLawsonFrame()
        self.checkKeyMotion(frame)
        return frame

    def jpgstream(self):
        #Used for mjpeg stream in server
        img = Image.fromarray(cv2.cvtColor(self(),cv2.COLOR_BGR2RGB))
        jpg = StringIO()
        img.save(jpg,'JPEG')
        return jpg.getvalue()

    def resizeToCalc(self,frame):
        return cv2.cvtColor(cv2.resize(frame,self.calcsize), cv2.COLOR_RGB2GRAY)

    def addkeymap(self,keyname,keyframe):
        """Given a mask for a key: save it!
        """
        print "Adding key",keyname
        f = keyframe.astype(np.float32)
        f = f/np.max(f)
        self.keys[keyname] = f

    def keyFromImage(self,imgfile,keyname=None):
        print "Loading file",imgfile
        img = cv2.imread(imgfile)

        img=self.resizeToCalc(img)
        self.addkeymap(os.path.basename(imgfile[:-4]),img)

    def loadGlob(self,g):
        files = glob.glob(g)
        for f in files:
            self.keyFromImage(f)

    def viewkey(self,key):
        #Shows the part of the image associated with a specific bitmap
        img = self.getLawsonFrame()
        f = self.resizeToCalc(img).astype(np.float32)
        f = f*self.keys[key]
        return cv2.cvtColor(tot.astype(np.uint8),cv2.COLOR_GRAY2RGB)

    def viewKeys(self):
        #Shows all keys at the same time in their own colors

        #The color map needs to be consistent
        if not (hasattr(self,"keycolors")):
            self.keycolors = {}

        img = self.getLawsonFrame()
        f = cv2.cvtColor(cv2.resize(img,self.calcsize), cv2.COLOR_RGB2GRAY).astype(np.float32)
        tot = np.zeros((self.calcsize[1],self.calcsize[0],3),dtype=np.float32)

        for k in self.keys:
            i  = f*self.keys[k]
            j = cv2.cvtColor(i.astype(np.uint8),cv2.COLOR_GRAY2RGB).astype(np.float32)

            if not (k in self.keycolors):
                self.keycolors[k] = uniform(size=3)

            color = self.keycolors[k]
            j[:,:,0] *= color[0]
            j[:,:,1] *= color[1]
            j[:,:,2] *= color[2]

            tot += j

        return (255.*tot/np.max(tot)).astype(np.uint8)

    def addCall(self,keyname,fnc,args=()):
        self.keyfnc[keyname] = (fnc,args)

    def fireKey(self,keyname):
        if (keyname in self.keyfnc):
            f = self.keyfnc[keyname]
            f[0](*f[1])

    def checkKeyMotion(self,frame):
        frame = self.resizeToCalc(frame)

        #This is the motion in the frame
        diff = cv2.absdiff(frame,self.oldframe)

        self.oldframe = frame

        for k in self.keys:
            #Get a normalized amount of motion from the key
            keymotion = self.multiplier*np.sum(diff*self.keys[k])/float(np.sum(self.keys[k]))/(1.0+self.keynorm[k])
            self.keyactivation[k] += keymotion

            self.keynorm[k] += keymotion*self.ndelta

            if (self.keyactivation[k] > 100.0):
                self.fireKey(k)
                for l in self.keys:
                    self.keyactivation[l] = 0.0
                break

        #Normalize the norm
        normmin = np.inf
        for k in self.keynorm:
            if (self.keynorm[k]< normmin):
                normmin = self.keynorm[k]
        for k in self.keynorm:
            self.keynorm[k] -= normmin

if (__name__=="__main__"):
    def keyme(key):
        print key


    c = LawsonCamera()

    c.loadGlob("./assets/keys/*.jpg")
    c.addCall("up",keyme,("up",))
    c.addCall("down",keyme,("down",))
    c.addCall("left",keyme,("left",))
    c.addCall("right",keyme,("right",))

    #c.start()
    c.start("http://128.10.29.32/mjpg/1/video.mjpg")
    print "Ready"
    while (1):
        img = c()

        cv2.imshow('s: save image, anything else: quit', img)
        k = cv2.waitKey(1)
        if (k==ord('s')):
            img = c.jpgstream()
            print c.keyactivation
            print "Writing image lwsn.jpg... (will freeze for a bit)"
            with open("lwsn.jpg","wb") as f:
                f.write(img)
            print "Finished writing"
        elif (k >0):
            break
