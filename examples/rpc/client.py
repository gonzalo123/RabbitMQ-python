import sys
sys.path.append("../../src")

from rabbit import builder

server = {
    'host': 'localhost',
    'port': 5672,
    'user': 'guest',
    'pass': 'guest',
}

print builder.rpc('rpc.hello', server).call("Gonzalo", "Ayuso")
