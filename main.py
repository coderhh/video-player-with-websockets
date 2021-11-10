import tkinter as tk
from tkinter import ttk
from video import VideoCapture
from PIL import ImageTk, Image
import cv2
import logging
from console_ui import ConsoleUi
from tkinter import ttk, VERTICAL, HORIZONTAL, N, S, E, W
import asyncio
import threading
import websockets

class App():
    def __init__(self, parent):
        self.parent = parent
        self.right_frame_width = 650
        self.right_frame_height = 400
        self.video_stream_widget = None
        self.logger_name = 'Server'
        self.init_logger()
        self.left_frame = tk.Frame(self.parent, width=200, heigh=300)
        self.left_frame.grid(row=0, column=0, padx=10, pady=5)
        self.left_frame.grid_propagate(False)

        self.right_frame = tk.Frame(self.parent, width=600, height=300)
        self.right_frame.grid(row=0, column=1, padx=10, pady=5)
        self.right_frame.grid_propagate(False)

        self.bottom_frame = tk.Frame(self.parent, width=800, height=300)
        self.bottom_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
        self.bottom_frame.grid_propagate(False)

        self.start_server_btn = ttk.Button(self.left_frame, text="Start Server", command=self.start_server)
        self.start_server_btn.grid(row=0, column=0, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        self.termiante_server_btn = ttk.Button(self.left_frame, text="Stop Server", command=self.stop_server)
        self.termiante_server_btn.grid(row=0, column=1, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        self.start_camera_btn = ttk.Button(self.left_frame, text = 'Start Camera', command=self.start_camera, state='normal')
        self.start_camera_btn.grid(row=1, column=0, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        self.stop_camera_btn = ttk.Button(self.left_frame, text = 'Stop Camera', command=self.stop_camera, state='normal')
        self.stop_camera_btn.grid(row=1, column=1, padx=5, pady=5, sticky='w'+'e'+'n'+'s')
        self.current_img = Image.open("Starship.jpg")
        self.resize_img =  self.current_img.resize((self.right_frame_width-10,self.right_frame_height-10), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(self.resize_img)

        self.img_lab = tk.Label(self.right_frame, image=self.image)
        self.img_lab.grid(row=0, column=0, padx=5, pady=5,sticky='w'+'e'+'n'+'s')

        self.console = ConsoleUi(self.bottom_frame, self.logger_name)

        self.consumer_queue = asyncio.Queue()
        self.producer_queue = asyncio.Queue()

        self._job = None

    def init_logger(self):
        # create logger
        self.logger = logging.getLogger(self.logger_name)
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

    def start_camera(self):
        self.logger.debug("Starting camera...")
        if self.video_stream_widget is not None:
            self.video_stream_widget.stop()
        self.video_stream_widget = VideoCapture(0).start()
        self.update()
    def update(self):
        frame = self.video_stream_widget.frame
        shape = frame.shape
        self.imgtk = ImageTk.PhotoImage(image = Image.fromarray(cv2.resize(frame,(shape[1],shape[0]))))
        self.img_lab.imgtk = self.imgtk
        self.img_lab.configure(image=self.imgtk)
        self._job = self.img_lab.after(10, self.update)
    def stop_camera(self):
        self.logger.debug("Stoping the camera..")
        self.video_stream_widget.stop()
        if self._job is not None:
            self.img_lab.after_cancel(self._job)
            self._job = None

    def start_server(self):
        self.logger.debug("Starting websockets server...")
        self.new_loop = asyncio.new_event_loop()
        self.t = threading.Thread(target=self.start_loop, args=(self.new_loop,))
        self.t.daemon = True
        self.t.start()
        asyncio.run_coroutine_threadsafe(self.start_ws_server(), self.new_loop)
    def start_loop(self,loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    async def start_ws_server(self):
        
        async with websockets.serve(self.handler, "localhost", 5678):
            self.logger.debug("Server Started")
            await asyncio.Future()  # run orefver

    async def handler(self, websocket, path):
        consumer_task = asyncio.create_task(
            self.consumer_handler(websocket, path))
        producer_task = asyncio.create_task(
            self.producer_handler(websocket, path))
        worker_task = asyncio.create_task(
            self.worker_hanlder(websocket,path))

        done, pending = await asyncio.wait(
            [consumer_task, producer_task, worker_task],
            return_when=asyncio.ALL_COMPLETED,
        )
        for task in pending:
            task.cancel()

    async def consumer_handler(self, websocket, path):
        async for message in websocket:
            await self.consumer(message)

    async def consumer(self, msg):
        await self.consumer_queue.put(msg)
        self.logger.info("Received:"+ msg)

    async def producer_handler(self,websocket, path):
        while True:
            message = await self.producer()
            if websocket != None and message != None:
                self.logger.debug(message)
                await websocket.send(message)

    async def producer(self):
        await asyncio.sleep(0.1)
        #self.logger.debug(self.consumer_queue.qsize())
        if self.producer_queue.qsize() > 0:
            msg = await self.producer_queue.get()
            if msg == 'start':
                self.logger.debug(msg)
                self.start_camera()
                return "CAMERA STARTED"
            elif msg == 'stop':
                self.logger.debug(msg)
                self.stop_camera()
                return "CAMERA STOP"
        return None

    async def worker_hanlder(self, websocket, path):
        while True:
            await asyncio.sleep(0.1)
            if self.consumer_queue.qsize() > 0:
                msg = await self.consumer_queue.get()
                #self.logger.error(msg)
                await self.producer_queue.put(msg)
                #self.logger.critical(msg)


    def stop_server(self):
        self.logger.debug("Stoping websockets server...")

# --- main ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title('WS RC Tool')
    root.wm_attributes("-topmost", 1)

    windowWidth = 850
    windowHeight = 500
    root.geometry("{}x{}".format(windowWidth, windowHeight))

    positionRight = int(root.winfo_screenwidth()/2 - windowWidth/2)
    positionDown = int(root.winfo_screenheight()/2 - windowHeight/2)

    root.geometry("+{}+{}".format(positionRight, positionDown))

    root.minsize(200, 200)
    root.resizable(1,1)

    app = App(root)
    root.mainloop()