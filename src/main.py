#! /usr/bin/python
"""
The entry module for FHT state reporter.

The overall architecture:
- FhtListener: listens to the FHT messages, splits them only to the basic components (address, message) and
                sends them to the Dispatcher
- Dispatcher: spawns the FhtListener and HttpServer, then waits for the messages from the FhtListener and
                interprets and send the data to the HttpServer that will allow it to constructs JSON to be
                sent to the web page
- HttpServer: runs webserver on port 80, gets information from Dispatcher
"""

import os
import sys
import logging
import time
from multiprocessing import Process, Queue
from fht_listener import FhtListener
from fht_analyzer import FhtAnalyzer
from http_server import HttpServer
from message import FhtMessage, HttpMessage


class Dispatcher(Process):
    """The main hub that translates messages from listner to server."""

    def __init__(self):
        """
        Init the instance variables, read the room ids.

        Read 
        """
        Process.__init__(self)
        self.listener_queue = None
        self.http_queue = None
        self.ids = {}
        idsf = open('../data/known_ids.txt', 'r')
        for l in idsf.readlines():
            if l[0] == '[':
                cur_room = l[1:-1]
            else:
                h = '{:02x}'.format(int(l[0:2])) + '{:02x}'.format(int(l[2:4]))
                self.ids[h.upper()] = cur_room

    def start(self):
        """
        Start the main loop of the application.

        Create instance of FhtListener and HttpServer and start them. Listen on the queue
        from the Listener and when receive the message, parse it and send the result to server.
        """
        self.listener_queue = Queue()
        listener = FhtListener(self.listener_queue)
        self.http_queue = Queue()
        http_server = HttpServer(self.http_queue)
        listener.start()
        http_server.start()

        while True:
            msg: FhtMessage = self.listener_queue.get()
            # process the message and create a message for http server
            self.analyze_msg(msg)

    def analyze_msg(self, msg):
        """
        Analyze the FHT message, produce message for HTTP server.

        ???
        """
        address = msg.address.upper()
        if address not in self.ids:
            logger.error("Unknown room %s", msg.address)
            return HttpMessage(address, HttpMessage.NEW_ROOM)
        data = FhtAnalyzer.AnalyzeMessage(msg)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                    filename='../data/main.log', level=logging.WARNING)
logger = logging.getLogger(__name__)
if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    logger.error("====================== START ===========================")
    fout = open('../data/stdout.log', 'a')
    ferr = open('../data/stderr.log', 'a')
    fout.write("---------------------------------------\n**** %s\n" % time.asctime())
    ferr.write("---------------------------------------\n**** %s\n" % time.asctime())
    sys.stdout = fout
    sys.stderr = ferr
    print('Starting')
    dispatcher = Dispatcher()
    dispatcher.start()
    # os.system("sudo shutdown -h now")
