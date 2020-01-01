#! /usr/bin/python

import sys
import os, os.path
from message import RoomIds, FhtMessage
from fht_analyzer import FhtAnalyzer

ids = RoomIds()

stats = {
    'count': 0,
    'room': {},
    'type': {},
    'command': {}
}
for i in ids.ids:
    if ids[i] not in stats['room']:
        stats['room'][ids[i]] = 0

interest = {
    'type': ['unknown', 'report1', 'report2'],
    'command': ['unknown']
}

ll = os.listdir('../data')
logs = [x for x in ll if len(x) == 29 and x[0:15] == 'fht_message_log']
for log in logs:
    logf = open(os.path.join('../data', log), 'r')
    for l in logf.readlines():
        msg = FhtMessage.read(l)
        if msg == None:
            # print("Invalid record: %s in %s", l, log)
            continue
        if len(msg.value) > 2:
            print(msg)
        pmsg = FhtAnalyzer.AnalyzeMessage(msg)
        stats['count'] += 1
        if msg.address in ids:
            room = ids[msg.address]
            stats['room'][room] += 1
        else:
            print('Unknown address: %s at %s' % (msg.address, log))
        for k in ['type', 'command']:
            if pmsg[k] not in stats[k]:
                stats[k][pmsg[k]] = 0
            stats[k][pmsg[k]] += 1
        for k in interest:
            for kw in interest[k]:
                if pmsg[k] == kw:
                    print("Interesting message of field %s with value %s on line %s in file %s" % (k, kw, l, log))

print(stats)

