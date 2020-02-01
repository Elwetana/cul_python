#! /usr/bin/python
"""Implementation of the FHT Listener."""

from multiprocessing import Process, Queue
import logging
import datetime
import RPi.GPIO as GPIO
import serial
from message import FhtMessage

logger = logging.getLogger(__name__)


class FhtListener(Process):
    """Listens for FHT messages and send them to dispatcher."""

    def __init__(self, queue: Queue):
        """
        Initialize the listener.

        Perform following operations:
        - pull down pin 17 to enable CUL board
        - open serial port
        - open message log for adding messages
        """
        Process.__init__(self)
        self.msg_queue = queue

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(17, GPIO.OUT)
        GPIO.output(17, GPIO.HIGH)

        self.port = serial.Serial("/dev/ttyAMA0", baudrate=38400, timeout=30.0)
        self.message_log_name = ""
        self.message_log = open("../data/fht_message_log.txt", "a")
        self.message_log.write("Starting the Listener process on %s\n" % datetime.datetime.now().isoformat())
        self.check_log()

    def check_log(self):
        """Check and rotate the log."""
        d = datetime.datetime.now()
        s = "{:04}{:02}{:02}-{:01}".format(d.year, d.month, d.day, d.hour // 4)
        if self.message_log_name != s:
            self.message_log.close()
            self.message_log_name = s
            self.message_log = open("../data/fht_message_log%s.txt" % self.message_log_name, "a")

    def run(self):
        r"""
        Inherited from Process.

        Start the main loop.
        """
        logger.warning("FHT listener running")
        self.port.write(b"X01\n")
        msg = b''
        while True:
            b = self.port.read()
            if b:
                msg += b
                if len(msg) > 1 and  msg[-1] == 10 and msg[-2] == 13:
                    m = self.parse_message(msg)
                    if m is None:
                        continue
                    self.check_log()
                    m.write(self.message_log)
                    logger.debug("Listener observed a message: %s", msg.decode("ascii"))
                    self.msg_queue.put(m)
                    msg = b''
                else:
                    # logger.error("Non standard length message received %s", msg.decode("ascii"))
                    pass
            else:
                logger.debug("timeout")
                pass  # timeout

    @staticmethod
    def parse_message(msg):
        """
        Convert bytes to message.

        Bytes received from the serial port are converted to string, last two bytes (new line) are
        stripped away, and the rest is used to create FhtMessage. The message we have received has
        the following structure:
        T<address><message type><command><parameter>
        where address is always 2 bytes, and message type, command and parameter are one byte
        NB: one byte is encoded in two characters in hex, so in characters, the raw format is:
        01234567890
        TAAAAMMCCPP
        T is literal, A is address, M is message type, C is command and P is parameter
        """
        msg = msg.decode("ascii")[:-2]
        if msg[0] != 'T':
            logger.error("Invalid message received: %s", msg)
            return None
        return FhtMessage(msg[1:5], msg[5:7], msg[7:9], msg[9:])


if __name__ == "__main__":
    print("FHT Listener class")
    logging.basicConfig(level=logging.DEBUG)
    msg_queue = Queue()  # type: Queue
    listener = FhtListener(msg_queue)
    listener.start()
    while True:
        pass
