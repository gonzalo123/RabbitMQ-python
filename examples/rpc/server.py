import sys
sys.path.append("../../src")

from rabbit import builder

server = {
    'host': 'localhost',
    'port': 5672,
    'user': 'guest',
    'pass': 'guest',
}

def onData(name, surname):
    builder.exchange('process.log', server).emit("rpc.start", 'rpc.hello')
    out = "Hello %s %s" % (name, surname)
    builder.exchange('process.log', server).emit("rpc.finish", 'rpc.hello')

    return out

builder.rpc('rpc.hello', server).server(onData)
