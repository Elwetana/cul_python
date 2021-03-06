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
from message import FhtMessage, HttpMessage, PayloadErrors, RoomIds


class Dispatcher(Process):
    """The main hub that translates messages from listner to server."""

    def __init__(self):
        """Init the instance variables, read the room ids."""
        Process.__init__(self)
        self.listener_queue = None
        self.http_queue = None
        self.roomIds = RoomIds()

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
            logger.debug("FHT message received")
            # process the message and create a message for http server
            http_msg = self.analyze_msg(msg)
            self.http_queue.put(http_msg)

    def analyze_msg(self, msg):
        """
        Analyze the FHT message, produce message for HTTP server.

        FhtAnalyzer returns a dictionary that we want to send to the HTTP server.
        We only check it for errors and set the error flags
        """
        error = PayloadErrors.OK
        payload = FhtAnalyzer.AnalyzeMessage(msg)
        address = msg.address.upper()
        room = address
        if address not in self.roomIds:
            logger.error("Unknown room %s", address)
            error |= PayloadErrors.NEW_ROOM
        else:
            room = self.roomIds[address]
        if payload["type"] == 'unknown':
            error |= PayloadErrors.NEW_TYPE
        if payload["command"] == 'unknown':
            error |= PayloadErrors.NEW_COMMAND
        if payload["warning"] == 'unknown':
            error |= PayloadErrors.NEW_WARNING
        return HttpMessage(room, error, payload)


logger = logging.getLogger(__name__)
if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                    filename='../data/main.log', level=logging.INFO)
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
