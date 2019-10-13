#! /usr/bin/python
"""Module for messages that are exchanged between processes."""
import datetime


class FhtMessage:
    """Class for sending data from FHT listener to Dispatcher."""

    def __init__(self, address, msg_type, command, value):
        """Constructor, initialize instance variables."""
        self.address = address
        self.msg_type = msg_type
        self.command = command
        self.value = value
        self.time = datetime.datetime.now().isoformat()

    def write(self, fout):
        """Write the message into file-like output."""
        fout.write("[%s] %s %s %s %s\n" % (self.time, self.address, self.msg_type, self.command, self.value))
        fout.flush()


class HttpMessage:
    """Class for sending info to HTTP server."""

    def __init__(self, room, error, payload):
        """Constructor, initialize instance variables."""
        self.room = room
        self.error = error
        self.payload = payload


class PayloadErrors:
    """Enum for errors that can happen when interpreting FHT messages."""

    OK = 0
    NEW_ROOM = 1
    NEW_TYPE = 2
    NEW_COMMAND = 4
    NEW_WARNING = 8
