import tkinter as tk
import queue
from tkinter.scrolledtext import ScrolledText
import logging
from queue_handler import QueueHandler
from tkinter import TOP

class ConsoleUi:
    """Poll messages from a logging queue and display them in a scrolled text widget"""
    def __init__(self, frame, logger_name):
        self.logger = logging.getLogger(logger_name)
        self.frame = frame
        # Create a ScrolledText wdiget
        self.scrolled_text = ScrolledText(self.frame, state='disabled', height=12)
        self.scrolled_text.pack(side=TOP)
        self.scrolled_text.configure(font='TkFixedFont')
        self.scrolled_text.tag_config('INFO', foreground='black')
        self.scrolled_text.tag_config('DEBUG', foreground='green')
        self.scrolled_text.tag_config('WARNING', foreground='orange')
        self.scrolled_text.tag_config('ERROR', foreground='red')
        self.scrolled_text.tag_config('CRITICAL', foreground='red', underline=1)
        # Create a logging handler using a queue
        self.log_queue = queue.Queue()
        self.queue_handler = QueueHandler(self.log_queue)
        formatter = logging.Formatter('%(asctime)s: %(message)s - %(filename)s --%(funcName)s')
        self.queue_handler.setFormatter(formatter)
        self.logger.addHandler(self.queue_handler)
        # Start polling messages from the queue
        self.poll_log_queue()
        #self.frame.after(100, self.poll_log_queue)
    def get_queue_status(self):
        qsize = self.log_queue.qsize()
        self.logger.info(qsize)
        self.frame.after(5000, self.get_queue_status)
    def display(self, record):
        msg = self.queue_handler.format(record)
        #print(msg)
        self.scrolled_text.configure(state='normal')
        self.scrolled_text.insert(tk.END, msg + '\n', record.levelname)
        self.scrolled_text.configure(state='disabled')
        # Autoscroll to the bottom
        self.scrolled_text.yview(tk.END)

    def poll_log_queue(self):
        # Check every 100ms if there is a new message in the queue to display
        #while True:
        if not self.log_queue.empty():
            try:
                record = self.log_queue.get(block=False)
            except queue.Empty:
               pass
            else:
                self.display(record)
        self.frame.after(100, self.poll_log_queue)