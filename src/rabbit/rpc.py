import pika
import json
import time
import uuid

class RPC:
    def __init__(self, name, conf):
        self.name = name
        self.conf = conf

    def call(self, *params):
        pika.PlainCredentials(self.conf['server']['user'], self.conf['server']['pass'])
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.conf['server']['host'], port=self.conf['server']['port']))
        channel = connection.channel()

        queueConf = self.conf['queue']
        result = channel.queue_declare(queue='', passive=queueConf['passive'], durable=queueConf['durable'], exclusive=queueConf['exclusive'], auto_delete=queueConf['autoDelete'])
        callback_queue = result.method.queue
        consumerConf = self.conf['consumer']
        channel.basic_consume(self.on_call_response, no_ack=consumerConf['noAck'], exclusive=consumerConf['exclusive'], queue='')

        self.response = None
        self.corr_id = str(uuid.uuid4())
        channel.basic_publish(exchange='', routing_key=self.name, properties=pika.BasicProperties(reply_to=callback_queue, correlation_id=self.corr_id), body=json.dumps(params))
        while self.response is None:
            connection.process_data_events()
        return self.response

    def on_call_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def server(self, callback):
        pika.PlainCredentials(self.conf['server']['user'], self.conf['server']['pass'])
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.conf['server']['host'], port=self.conf['server']['port']))
        channel = connection.channel()

        queueConf = self.conf['queue']
        channel.queue_declare(self.name, passive=queueConf['passive'], durable=queueConf['durable'], exclusive=queueConf['exclusive'], auto_delete=queueConf['autoDelete'])

        channel.basic_qos(prefetch_count=1)
        consumerConf = self.conf['consumer']

        def on_server_request(ch, method, props, body):
            response = callback(*json.loads(body))

            ch.basic_publish(exchange='', routing_key=props.reply_to, properties=pika.BasicProperties(correlation_id=props.correlation_id), body=json.dumps(response))
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print "%s %s::req => '%s' response => '%s'" % (time.strftime("[%d/%m/%Y-%H:%M:%S]", time.localtime(time.time())), self.name, body, response)

        channel.basic_consume(on_server_request, queue=self.name, no_ack=consumerConf['noAck'], exclusive=consumerConf['exclusive'])

        print "%s RPC '%s' initialized" % (time.strftime("[%d/%m/%Y-%H:%M:%S]", time.localtime(time.time())), self.name)
        channel.start_consuming()
