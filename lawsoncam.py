import cv2
from PIL import Image
from cStringIO import StringIO

class LawsonCamera(object):
    """Given box locations of different keys, allows to use the webcam as a controller"""
    def __init__(self,address="rtsp://128.10.29.32:554/axis-media/media.amp?videocodec=h264&amp;camera=1&amp;streamprofile=Bandwidth"):
        self.stream = cv2.VideoCapture(address)
        self.keys = {}
    def getFrame(self):
        ret, frame = self.stream.read()
        return frame
    
    def getLawsonFrame(self):
        #Lawson's cameras have a black strip above video feed - remove the strip
        return self.getFrame()[24:]

    def __call__(self,retjpeg=False):
        return self.getLawsonFrame()
    def jpgstream(self):
        img = Image.fromarray(cv2.cvtColor(self(),cv2.COLOR_BGR2RGB))
        jpg = StringIO()
        img.save(jpg,'JPEG')
        return jpg.getvalue()


        
        

if (__name__=="__main__"):
    #c = LawsonCamera("http://128.10.29.32/mjpg/1/video.mjpg")
    c = LawsonCamera()
    while (1):
        img = c()
        cv2.imshow('VIDEO', img)
        if (cv2.waitKey(1)>0):
            break
