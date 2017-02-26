import sys
sys.path.append("../../src")

from rabbit import builder

server = {
    'host': 'localhost',
    'port': 5672,
    'user': 'guest',
    'pass': 'guest',
}

exchange = builder.exchange('process.log', server)

def onData(routingKey, data):
    print routingKey, data

exchange.receive("exchange.finish", onData)
