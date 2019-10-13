#! /usr/bin/python
"""Class for analyzing FHT messages received by listener."""

import logging
from message import FhtMessage

logger = logging.getLogger(__name__)


class FhtAnalyzer:
    """Static class for analyzing messages from listener."""

    message_types = {
        "00": "all-valves",
        "41": "desired-temp",
        "42": "measured-low",
        "43": "measured-high",
        "44": "warnings"
    }

    conversions = {
        "all-valves": lambda data: data * 100.0 / 255.0,
        "desired-temp": lambda data: data / 2.0,
        "measured-low": lambda data: data * 0.1,
        "measured-high": lambda data: data * 25.5
    }

    warnings = [
        'OK',
        'BATT LOW',
        'TEMP LOW',
        'WINDOW OPEN',
        'WINDOW ERR'
    ]

    commands = {
        "6": "set-valve",
        "9": "special",
        "A": "set-valve A"
    }

    flags = {
        1: 'batt-allowed',      # valve can weep about the low battery
        2: 'extended',          # always set
        4: 'bidirectional',     # message from thermostat to the FHZ central unit
        8: 'repetitions'        # this is a repetition of previous signal
    }

    @staticmethod
    def AnalyzeMessage(msg: FhtMessage):
        """
        Translate the raw hex values to their actual values.

        The list of 'message types' (technically, it's subaddresses) we know is
        in the dictionary message_types. Whenever we discover a new one, we add
        it there.
        The command part of the original message actually has to be split into
        low and high part of the byte -- in hexa it's simple, we just take the
        first and second character. The second character (lower 4 bits) is the
        actual command, the first character (high 4 bits) is set of flags.
        """
        logger.debug("Analyzing a message")
        msg_type = 'unknown'
        if msg.msg_type in FhtAnalyzer.message_types:
            msg_type = FhtAnalyzer.message_types[msg.msg_type]
        else:
            logger.error("New message type %s", msg.msg_type)
        value = 0.0
        if msg_type in FhtAnalyzer.conversions:
            value = FhtAnalyzer.conversions[msg_type](int(msg.value, 16))
        warning = ''
        if msg_type == "warnings":
            warningIndex = int(msg.value, 16)
            if warningIndex < len(FhtAnalyzer.warnings):
                warning = FhtAnalyzer.warnings[warningIndex]
            else:
                warning = 'unknown'
                logger.error('Unknown warning index: %s', warningIndex)
        command = 'unknown'
        if msg.command[1] in FhtAnalyzer.commands:
            command = FhtAnalyzer.commands[msg.command[1]]
        else:
            logger.error("Unknown command: %s", msg.command[1])
        flags = []
        for i in range(4):
            f = int(msg.command[0], 16) & (1 << i)
            if f in FhtAnalyzer.flags:
                flags.append(FhtAnalyzer.flags[f])
        logger.debug("Analysis complete")
        return {
            'type': msg_type,
            'value': value,
            'warning': warning,
            'command': command,
            'flags': flags
        }

if __name__ == "__main__":
    msg = FhtAnalyzer.AnalyzeMessage(FhtMessage("FFFF", "00", "AA", "00"))
    print(msg)
