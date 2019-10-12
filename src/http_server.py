#! /usr/bin/python
"""Implementation of the HTTP server."""

import sys
from multiprocessing import Queue, Process
from queue import Empty
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
from json import dumps
# from message import HttpMsg
import time
from typing import Dict

logger = logging.getLogger(__name__)


class HttpHandler(BaseHTTPRequestHandler):
    """Implements the do_GET for handling HTTP requests."""

    configRoot = '../http'
    dataRoot = '../data'

    state: Dict[str, int] = {}

    def do_GET(self):
        """
        Serve data to client.

        We only now how to server two kinds of data: the basic webpage and the JSON with data
        If we are asked for JSON specifically, we return than, in all other cases we return
        the basic page.
        """
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        if self.path == '/fht_data.json':
            self.wfile.write(bytes(self.get_json(), 'utf-8'))
            return

        # f = open(HttpHandler.configRoot + 'index.html')
        # HACK
        with open('z:\\www\\pustik\\fht_index.html') as f:
            # /HACK
            html = f.read()
        self.wfile.write(bytes(html, 'utf-8'))

    def get_json(self):
        """
        Send the client JSON with all data.

        JSON file structure:
        {
            <room_name>: {
                'last_all': [
                    {'cmnd': value}, ... # last five messages
                ],

            }
        }
        """
        return dumps(self.state)


class HttpServer(Process):

    serverPort = 80
    timeout = 0.1

    def __init__(self, queue: Queue):
        """
        Create HTTP server to display the web page with current status of FHT devices.

        :param queue: queue for receiving data from the process that reads serial port
        """
        Process.__init__(self)
        self.msg_queue = queue
        self.server = None

    def run(self):
        """
        Start the server main loop.

        We check for a new request with HttpServer.timeout, than we check for
        a new message from dispatcher and add it to our state.
        """
        self.server = HTTPServer(('', HttpServer.serverPort), HttpHandler)
        self.server.timeout = HttpServer.timeout
        self.server.msg_queue = self.msg_queue
        logger.warning("HTTP server running")
        try:
            while True:
                self.server.handle_request()
                try:
                    msg = self.msg_queue.get(False)
                    HttpHandler.state += msg['payload']
                except Empty:
                    pass
        except Exception:
            print(sys.exc_info())

        logger.warning("HTTP server terminating")


if __name__ == "__main__":
    print("HTTP server class")
    logging.basicConfig(level=logging.INFO)
    msg_queue = Queue()  # type: Queue
    server = HttpServer(msg_queue)
    server.start()
    while True:
        time.sleep(5)
        msg_queue.put({'payload': 1})
