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

exchange.emit("xxx.log", "aaaa")
exchange.emit("xxx.log", ["11", "aaaa"])
exchange.emit("yyy.log", "aaaa")
