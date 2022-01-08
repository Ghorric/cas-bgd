from streaming.event_consumer import *
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer
from confluent_kafka import SerializingProducer


def create_value_serializer(conf, topic) -> AvroSerializer:
    schema_registry_conf = {
        'url': conf['schema.registry.url'],
        'basic.auth.user.info': conf['basic.auth.user.info']}
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    schema_id = schema_registry_client.get_latest_version(f'{topic}-value').schema_id
    schema_val = schema_registry_client.get_schema(schema_id)
    print(f'schema_id={schema_id}, schema_str={schema_val.schema_str}, schema_type={schema_val.schema_type}')
    value_avro_serializer = AvroSerializer(schema_registry_client,
                                               schema_val.schema_str)
    return value_avro_serializer


def create_key_serializer() -> StringSerializer:
    return StringSerializer()


def create_kafka_producer(
        key_serializer,
        value_serializer,
        config) -> SerializingProducer:
    producer_conf = dict(config)
    for key in ['schema.registry.url', 'basic.auth.user.info', 'basic.auth.credentials.source']:
        producer_conf.pop(key, None)
    producer_conf['key.serializer'] = key_serializer
    producer_conf['value.serializer'] = value_serializer

    kafka_producer = SerializingProducer(producer_conf)
    return kafka_producer

def acked(err, msg):
    if err is not None:
        print(f"Delivery failed: {err}")
    else:
        print(f"Event {msg.key()} created for topic: {msg.topic()}")


def create_producer_topic_name(consumer_topic):
    return f'{consumer_topic}-out'


def init(config, consumer_topic) -> SerializingProducer:
    return create_kafka_producer(
        create_key_serializer(),
        create_value_serializer(config, create_producer_topic_name(consumer_topic)),
        config)


def produce_event(kafka_producer: SerializingProducer, consumer_topic, event_key, event_value):
    producer_topic = create_producer_topic_name(consumer_topic)
    # print(f'Start producing event: {event_key}')
    kafka_producer.produce(topic=producer_topic, key=event_key, value=event_value, on_delivery=acked)
    kafka_producer.flush()
    print(f'Event sent {event_key} to topic {producer_topic}')
