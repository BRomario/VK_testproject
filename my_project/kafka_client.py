from confluent_kafka import Producer, Consumer, KafkaException
import json

KAFKA_BROKER_URL = '127.0.0.1:9092'
KAFKA_TOPIC = 'engine_topic'

producer = Producer({'bootstrap.servers': KAFKA_BROKER_URL})


def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


def send_message(message):
    producer.produce(KAFKA_TOPIC, json.dumps(message).encode('utf-8'), callback=delivery_report)
    producer.poll(0)
    producer.flush()


consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKER_URL,
    'group.id': 'mygroup',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe([KAFKA_TOPIC])


def consume_messages():
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print('%% %s [%d] reached end at offset %d\n' %
                          (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                print('Received message: {}'.format(msg.value().decode('utf-8')))
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
