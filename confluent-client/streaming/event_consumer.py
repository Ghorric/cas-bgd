import datetime
from typing import Callable
from confluent_kafka import DeserializingConsumer
from confluent_kafka.avro import SerializerError
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.serialization import StringDeserializer
from confluent_kafka.schema_registry.avro import AvroDeserializer

import common.util as util

class CutStartingBytesStringDeserializer(StringDeserializer):
    def __init__(self, codec='utf_8'):
        super().__init__(codec)

    def __call__(self, value, ctx):
        if len(value) >= 6:
            value = value[6:]
        return super().__call__(value, ctx)


def read_args():
    return util.parse_args()


def read_args_consumer():
    a = read_args()
    return util.read_kafka_config_file(a.config_file), \
           a.topic, \
           a.continue_consuming


def create_key_deserializer() -> StringDeserializer:
    return CutStartingBytesStringDeserializer()


def create_value_deserializer(conf, topic) -> AvroDeserializer:
    schema_registry_conf = {
        'url': conf['schema.registry.url'],
        'basic.auth.user.info': conf['basic.auth.user.info']}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    schema_id = schema_registry_client.get_latest_version(f'{topic}-value').schema_id
    schema_val = schema_registry_client.get_schema(schema_id)
    print(f'schema_id={schema_id}, schema_str={schema_val.schema_str}, schema_type={schema_val.schema_type}')
    value_avro_deserializer = AvroDeserializer(schema_registry_client,
                                               schema_val.schema_str)
    return value_avro_deserializer


def datetime_now() -> str:
    return datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')


def create_kafka_consumer(
        key_deserializer,
        value_deserializer,
        conf,
        topic,
        offset='latest',
        group_id=None) -> DeserializingConsumer:
    consumer_conf = dict(conf)
    for key in ['schema.registry.url', 'basic.auth.user.info', 'basic.auth.credentials.source']:
        consumer_conf.pop(key, None)
    consumer_conf['key.deserializer'] = key_deserializer
    consumer_conf['value.deserializer'] = value_deserializer
    if not group_id:
        group_id = f'{topic}_group'
    if offset == 'beginning':
        group_id = f'{group_id}_{datetime_now()}'
    consumer_conf['group.id'] = group_id
    consumer_conf['auto.offset.reset'] = offset
    kafka_consumer = DeserializingConsumer(consumer_conf)
    kafka_consumer.subscribe([topic])
    return kafka_consumer


# Process events
def start_consuming(
        consumer: DeserializingConsumer,
        event_received_func: Callable[[str, object], None],
        continue_consuming_func=lambda i: True):
    index = 0
    while continue_consuming_func(index):
        index += 1
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                # No message available within timeout.
                # Initial message consumption may take up to
                # `session.timeout.ms` for the consumer group to
                # rebalance and start consuming
                print("Waiting for message or event/error in poll()")
                continue
            elif msg.error():
                print('error: {}'.format(msg.error()))
            else:
                key = msg.key()
                val = msg.value()
                # print(fevent_consumer => 'key={key}, value={val}')
                event_received_func(key, val)
        except KeyboardInterrupt:
            break
        except SerializerError as e:
            # Report malformed record, discard results, continue polling
            print("Message deserialization failed {}".format(e))
            pass
    consumer.close()


if __name__ == '__main__':
    conf, topic, continue_consuming = read_args_consumer()
    c = create_kafka_consumer(create_key_deserializer(),
                              create_value_deserializer(conf, topic),
                              conf,
                              topic,
                              'beginning')
    start_consuming(c, lambda key, val: print(f'{key}={val}'))


