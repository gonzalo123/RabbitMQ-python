import sys
sys.path.append("../../src")

from rabbit import builder

server = {
    'host': 'localhost',
    'port': 5672,
    'user': 'guest',
    'pass': 'guest',
}

queueName = 'queue'
queue = builder.queue(queueName, server)

def onData(data):
    builder.exchange('process.log', server).emit("exchange.start", queueName)
    builder.exchange('process.log', server).emit("exchange.finish", queueName)

queue.receive(onData)
