from queue import Queue
import cv2
from threading import Thread
from datetime import datetime
import numpy as np
import logging

class VideoCapture:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """
    def __init__(self, video_source=0):
        # Open the video source
        self.stream = cv2.VideoCapture(video_source)
        self.get_thread = None
        if not self.stream.isOpened():
            raise ValueError("Unable to open video source", video_source)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        # Get video source width and height
        self.width = self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.imgQueue = Queue()
         # create logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - ProcessName: %(processName)s - ThreadName: %(threadName)s - FunctionName: %(funcName)s - Level: %(levelname)s - Message: %(message)s")
        # add formatter to ch
        ch.setFormatter(formatter)
        # add ch to logger
        self.logger.addHandler(ch)

    def start(self):
        self.get_thread = Thread(target=self.get, args=())
        self.get_thread.daemon = True
        self.get_thread.start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed, self.frame) = self.stream.read()
                if self.grabbed:
                    self.frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    
                    #self.logger.info(str(self.width) + ","+ str(self.height))
                    scale_percent = 10 # percent of original size
                    width = int(self.frame.shape[1] * scale_percent / 100)
                    height = int(self.frame.shape[0] * scale_percent / 100)
                    dim = (width, height)
                    # resize image
                    self.frame = cv2.resize(self.frame, dim, interpolation = cv2.INTER_AREA)
                    cv2.putText(self.frame, str(datetime.now()),(10,30), font, 1,(255,255,255),2,cv2.LINE_AA)
                    #self.logger.info(str(width) + ","+ str(height))
                    # if self.imgQueue.qsize() > 19:
                    #     f = self.imgQueue.get()
                    self.imgQueue.put(self.frame)
                    self.logger.info(self.imgQueue.qsize())
    def read(self):
        if not self.imgQueue.empty():
            currentFrame = self.imgQueue.get()
            return currentFrame           
                    
    def stop(self):
        self.stopped = True

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.stream.isOpened():
            self.stream.release()