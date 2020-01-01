#! /usr/bin/python
"""Module for messages that are exchanged between processes."""
import datetime


class FhtMessage:
    """Class for sending data from FHT listener to Dispatcher."""

    def __init__(self, address, msg_type, command, value, time=None):
        """Constructor, initialize instance variables."""
        self.address = address
        self.msg_type = msg_type
        self.command = command
        self.value = value
        if time == None:
            self.time = datetime.datetime.now().isoformat()
        else:
            self.time = time

    def write(self, fout):
        """Write the message into file-like output."""
        fout.write("[%s] %s %s %s %s\n" % (self.time, self.address, self.msg_type, self.command, self.value))
        fout.flush()

    def __str__(self):
        return "Msg address: %s, type: %s, command: %s, value: %s" % (self.address, self.msg_type, self.command, self.value)

    @classmethod
    def read(cls, l):
        l = l.strip()
        if(len(l) > 40):
            t = datetime.datetime.fromisoformat(l[1:27])
            address = l[29:33]
            msg_type = l[34:36]
            command = l[37:39]
            value = l[40:]
            return cls(address, msg_type, command, value, t)
        else:
            return None



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


class RoomIds:

    def __init__(self):
        self.ids = {}
        idsf = open('../data/known_ids.txt', 'r')
        for l in idsf.readlines():
            l = l.strip()
            if l[0] == '[':
                cur_room = l[1:-1]
            else:
                h = '{:02x}'.format(int(l[0:2])) + '{:02x}'.format(int(l[2:4]))
                self.ids[h.upper()] = cur_room

    def __getitem__(self, key):
        return self.ids[key]

    def __contains__(self, key):
        return key in self.ids


if __name__ == "__main__":
    r = RoomIds()
    if "6004" in r:
        print(r["6004"])
    f = open("../data/fht_message_log20191229-5.txt", "r")
    l = f.readline()
    m = FhtMessage.read(l)
    print(m)

