import pika
import json
import time

class Queue:
    def __init__(self, name, conf):
        self.name = name
        self.conf = conf

    def emit(self, data=None):
        credentials = pika.PlainCredentials(self.conf['server']['user'], self.conf['server']['pass'])
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.conf['server']['host'], port=self.conf['server']['port'], credentials=credentials))
        channel = connection.channel()

        queueConf = self.conf['queue']
        channel.queue_declare(queue=self.name, passive=queueConf['passive'], durable=queueConf['durable'], exclusive=queueConf['exclusive'], auto_delete=queueConf['autoDelete'])

        channel.basic_publish(exchange='', routing_key=self.name, body=json.dumps(data), properties=pika.BasicProperties(delivery_mode=2))
        connection.close()

    def receive(self, callback):
        credentials = pika.PlainCredentials(self.conf['server']['user'], self.conf['server']['pass'])
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.conf['server']['host'], port=self.conf['server']['port'], credentials=credentials))
        channel = connection.channel()

        queueConf = self.conf['queue']
        channel.queue_declare(queue=self.name, passive=queueConf['passive'], durable=queueConf['durable'], exclusive=queueConf['exclusive'], auto_delete=queueConf['autoDelete'])

        def _callback(ch, method, properties, body):
            callback(json.loads(body))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print "%s %s::%s" % (time.strftime("[%d/%m/%Y-%H:%M:%S]", time.localtime(time.time())), self.name, body)

        print "%s Queue '%s' initialized" % (time.strftime("[%d/%m/%Y-%H:%M:%S]", time.localtime(time.time())), self.name)
        consumerConf = self.conf['consumer']
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(_callback, self.name, no_ack=consumerConf['noAck'], exclusive=consumerConf['exclusive'])

        channel.start_consuming()
