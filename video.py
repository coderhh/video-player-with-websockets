import cv2
from threading import Thread
from datetime import datetime

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
                    cv2.putText(self.frame, str(datetime.now()),(10,30), font, 1,(255,255,255),2,cv2.LINE_AA)
    def stop(self):
        self.stopped = True

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.stream.isOpened():
            self.stream.release()