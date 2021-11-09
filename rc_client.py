from tkinter import *
from tkinter import ttk
import websockets
import threading
import logging
import asyncio
from console_ui import ConsoleUi
try:
    import thread
except ImportError:
    import _thread as thread

class Client():

    def __init__(self, parent) -> None:
        self.parent = parent
        ###############################Logger##############################################
        # create logger
        self.logger_name = "Client"
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
        self.frm = ttk.Frame(root, padding=10)
        self.frm.pack(fill=BOTH, expand=True)
        ttk.Button(self.frm, text="Connect", command=self.connect).pack(side=TOP)
        ttk.Label(self.frm, text="Message:").pack(side=TOP)
        self.textMsg = ttk.Entry(self.frm, width=13)
        self.textMsg.pack(side=TOP)
        ttk.Button(self.frm, text="Send", command=self.send).pack(side=TOP)
        self.console = ConsoleUi(self.frm, self.logger_name)

    def connect(self):
        self.logger.debug("Connecting to websocket server")
        async def connect_to_ws():
            uri = "ws://localhost:5678"
            socket = await websockets.connect(uri)
            self.ws = socket
            while True:
                msg = await self.ws.recv()
                self.logger.debug(msg)
        loop = asyncio.new_event_loop()
        t = threading.Thread(target=self.start_background_loop, args=(loop,), daemon=True)
        t.start()
        asyncio.run_coroutine_threadsafe(connect_to_ws(), loop)

    def start_background_loop(self,loop: asyncio.AbstractEventLoop) -> None:
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def send(self):
        msg =  self.textMsg.get()
        async def async_send(msg):
            self.logger.info(msg)
            await self.ws.send(msg)
        loop = asyncio.new_event_loop()
        t = threading.Thread(target=self.start_background_loop, args=(loop,), daemon=True)
        t.start()
        asyncio.run_coroutine_threadsafe(async_send(msg), loop)

if __name__ == "__main__":
    root = Tk()
    root.title('WebSockets Client Demo')
    root.wm_attributes("-topmost", 1)
    root.geometry("600x300+300+600")
    app = Client(root)
    root.mainloop()