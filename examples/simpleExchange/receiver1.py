import sys
sys.path.append("../../src")

from rabbit import builder

server = {
    'host': 'localhost',
    'port': 5672,
    'user': 'guest',
    'pass': 'guest',
}

def onData(routingKey, data):
    print routingKey, data

builder.exchange('process.log', server).receive("yyy.log", onData)
