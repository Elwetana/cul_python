#! /usr/bin/python
"""Class for analyzing FHT messages received by listener."""

import logging
from message import FhtMessage

logger = logging.getLogger(__name__)


class FhtAnalyzer:
    """Static class for analyzing messages from listener."""

    message_types = {
        "00": "all-valves",

        "14": "mon-from1",
        "15": "mon-to1",
        "16": "mon-from2",
        "17": "mon-to2",
        "18": "tue-from1",
        "19": "tue-to1",
        "1A": "tue-from2",
        "1B": "tue-to2",
        "1C": "wed-from1",
        "1D": "wed-to1",
        "1E": "wed-from2",
        "1F": "wed-to2",
        "20": "thu-from1",
        "21": "thu-to1",
        "22": "thu-from2",
        "23": "thu-to2",
        "24": "fri-from1",
        "25": "fri-to1",
        "26": "fri-from2",
        "27": "fri-to2",
        "28": "sat-from1",
        "29": "sat-to1",
        "2A": "sat-from2",
        "2B": "sat-to2",
        "2C": "sun-from1",
        "2D": "sun-to1",
        "2E": "sun-from2",
        "2F": "sun-to2",

        "3E": "mode",

        "41": "desired-temp",
        "42": "measured-low",
        "43": "measured-high",
        "44": "warnings",
        "4B": "ack",
        "60": "year",
        "61": "month",
        "62": "day",
        "63": "hour",
        "64": "minute",

        "65": "report1",
        "66": "report2",

        "82": "day-temp",
        "84": "night-temp",
        "85": "lowtemp-offset",  # Alarm-Temp.-Differenz
        "8A": "windowopen-temp",
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
            logger.error("New message type %s, cmnd: %s, val: %s", msg.msg_type, msg.command, msg.value)
        try:
            value = int(msg.value, 16)
        except (ValueError, TypeError):
            value = 0
        if msg_type in FhtAnalyzer.conversions:
            value = FhtAnalyzer.conversions[msg_type](value)
        warning = ''
        if msg_type == "warnings":
            warningIndex = int(msg.value, 16)
            if warningIndex < len(FhtAnalyzer.warnings):
                warning = FhtAnalyzer.warnings[warningIndex]
            else:
                warning = 'unknown'
                logger.error('Unknown warning index: %s', warningIndex)
        command = 'unknown'
        if (len(msg.command) > 1) and (msg.command[1] in FhtAnalyzer.commands):
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
