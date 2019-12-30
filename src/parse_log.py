#! /usr/bin/python

import sys
from message import RoomIds

ids = RoomIds()






log = open('../data/log.txt', 'r')

cmd = {}
for l in log.readlines():
    a = l.split(' ')
    if a[2] != 'T':
        print(l, a)
        print("INVALID LOG")
        sys.exit(1)
    t = a[1]
    address = a[3]
    sub_address = a[4]
    command = a[5]
    if address not in cmd:
        cmd[address] = {}
    if sub_address not in cmd[address]:
        cmd[address][sub_address] = []
    cmd[address][sub_address].append((t, command))
log.close()
print("Count:", len(cmd))
for address in cmd:
    print("--", int(address[0:2], 16), int(address[2:4], 16),)
    if address in ids:
        print(ids[address])
    else:
        print("unknown")
    for sub_address in cmd[address]:
        print("  Sub address", sub_address)
        for c in cmd[address][sub_address]:
            print("      ", c[0],  c[1][0:4])
