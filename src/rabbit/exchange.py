import pika
import json
import time

class Exchange:
    def __init__(self, name, conf):
        self.name = name
        self.conf = conf

    def emit(self, routingKey, data=None):
        credentials = pika.PlainCredentials(self.conf['server']['user'], self.conf['server']['pass'])
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.conf['server']['host'], port=self.conf['server']['port'], credentials=credentials))
        channel = connection.channel()

        exchangeConf = self.conf['exchange']
        channel.exchange_declare(exchange=self.name, type='topic', passive=exchangeConf['passive'], durable=exchangeConf['durable'], auto_delete=exchangeConf['autoDelete'], internal=exchangeConf['internal'])
        channel.basic_publish(exchange=self.name, routing_key=routingKey, body=json.dumps(data))
        connection.close()

    def receive(self, bindingKey, callback):
        credentials = pika.PlainCredentials(self.conf['server']['user'], self.conf['server']['pass'])
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.conf['server']['host'], port=self.conf['server']['port'], credentials=credentials))
        channel = connection.channel()

        exchangeConf = self.conf['exchange']
        channel.exchange_declare(exchange=self.name, type='topic', passive=exchangeConf['passive'], durable=exchangeConf['durable'], auto_delete=exchangeConf['autoDelete'], internal=exchangeConf['internal'])

        queueConf = self.conf['queue']
        result = channel.queue_declare(passive=queueConf['passive'], durable=queueConf['durable'], exclusive=queueConf['exclusive'], auto_delete=queueConf['autoDelete'])
        queue_name = result.method.queue

        channel.queue_bind(exchange=self.name, queue=queue_name, routing_key=bindingKey)

        print "%s Exchange '%s' initialized" % (time.strftime("[%d/%m/%Y-%H:%M:%S]", time.localtime(time.time())), self.name)

        def _callback(ch, method, properties, body):
            callback(method.routing_key, json.loads(body))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print "%s %s:::%s" % (time.strftime("[%d/%m/%Y-%H:%M:%S]", time.localtime(time.time())), self.name, body)

        consumerConf = self.conf['consumer']
        channel.basic_consume(_callback, queue=queue_name, no_ack=consumerConf['noAck'], exclusive=consumerConf['exclusive'])
        channel.start_consuming()
