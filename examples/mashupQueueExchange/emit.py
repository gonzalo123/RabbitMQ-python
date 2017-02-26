import sys
sys.path.append("../../src")

from rabbit import builder

server = {
    'host': 'localhost',
    'port': 5672,
    'user': 'guest',
    'pass': 'guest',
}

queue = builder.queue('queue', server)

queue.emit({'aaa': 1})
queue.emit({'aaa': 2})
queue.emit({'aaa': 3})
