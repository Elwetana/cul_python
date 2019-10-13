#! /usr/bin/python
"""Implementation of the HTTP server."""

import sys
import logging
import os.path
from time import sleep
from multiprocessing import Queue, Process
from queue import Empty
from http.server import BaseHTTPRequestHandler, HTTPServer
from json import dumps
from typing import Dict, Any
from message import HttpMessage

logger = logging.getLogger(__name__)


class HttpHandler(BaseHTTPRequestHandler):
    """Implements the do_GET for handling HTTP requests."""

    configRoot = '../http'

    MSG_TO_KEEP = 5
    state: Dict[str, Any] = {'errors': []}

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
        else:
            with open(os.path.join(HttpHandler.configRoot, 'index.html')) as f:
                html = f.read()
            self.wfile.write(bytes(html, 'utf-8'))

    def get_json(self):
        """
        Send the client JSON with all data.

        JSON file structure:
        {
            <room_name>: {
                <msg_type>: [
                    {<cmnd>: value, 'flags': [...]}, ... # last five messages of this type
                ],
                ...
            },
            ...
            'errors': [list of errors]
        }
        """
        return dumps(HttpHandler.state)


class HttpServer(Process):
    """HTTP Server process, receives messages from dispatcher."""

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
                    msg: HttpMessage = self.msg_queue.get(False)
                    self.update_state(msg)
                    logger.debug("HTTP message received")
                except Empty:
                    pass
        except Exception:
            print(sys.exc_info())

        logger.warning("HTTP server terminating")

    def update_state(self, msg: HttpMessage):
        """Update HttpHandler state with values from the message we received."""
        if msg.room not in HttpHandler.state:
            HttpHandler.state[msg.room] = {}
        if msg.payload['type'] not in HttpHandler.state[msg.room]:
            HttpHandler.state[msg.room][msg.payload['type']] = []
        if len(HttpHandler.state[msg.room][msg.payload['type']]) >= HttpHandler.MSG_TO_KEEP:
            del HttpHandler.state[msg.room][msg.payload['type']][0]
        value = msg.payload['value']
        if msg.payload['type'] == 'warnings':
            value = msg.payload['warning']
        HttpHandler.state[msg.room][msg.payload['type']].append({
            msg.payload['command']: value,
            'flags': msg.payload['flags']
        })
        if msg.error != 0:
            HttpHandler.state['errors'].append(msg.error)


if __name__ == "__main__":
    print("HTTP server class")
    logging.basicConfig(level=logging.INFO)
    msg_queue = Queue()  # type: Queue
    server = HttpServer(msg_queue)
    server.start()
    while True:
        sleep(5)
        msg_queue.put(HttpMessage(
            'main room',
            0,
            {
                'type': 'all-valves',
                'value': 0.0,
                'warning': '',
                'command': 'set-valve',
                'flags': ['extended', 'repetitions']
            }
        ))
