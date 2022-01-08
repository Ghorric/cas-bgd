import os
import redis
from dataclasses import dataclass
import json

import mapstore.redis_service as redis_service
import streaming.event_consumer as event_consumer
import streaming.event_producer as event_producer
import labels.google_vision as google_vision
from google.cloud import vision
from confluent_kafka import SerializingProducer

@dataclass
class Setup:
    redis_client: redis.StrictRedis
    vision_client: vision.ImageAnnotatorClient
    pexel_token: str
    kafka_config: dict
    topic: str
    continue_consuming_str: str
    event_handlers: dict
    offset: str
    redis_tbl_name: str
    redis_json_tbl_name: str


def create_streaming_consumer(conf, topic, offset):
    key_deserializer = event_consumer.create_key_deserializer()
    value_deserializer = event_consumer.create_value_deserializer(conf, topic)
    return event_consumer.create_kafka_consumer(key_deserializer, value_deserializer, conf, topic, offset)


def get_pexel_token():
    tkn = os.environ.get('PEXEL_TOKEN', 'UNKNOWN')
    print(f'pexel_token={tkn}')
    if not tkn or not tkn.strip() or tkn.strip() == 'UNKNOWN':
        raise Exception('PEXEL_TOKEN not set')
    return tkn


def create_vision_client():
    vision_secret_path = google_vision.parse_args().vision_config
    print(f'vision_secret_path: {vision_secret_path}')
    return google_vision.create_client(vision_secret_path)


def detect_image_labels(setup: Setup, uri: str) -> dict:
    labels = google_vision.detect_labels(
        setup.vision_client,
        google_vision.pexel_request(uri, setup.pexel_token))
    print(f'detect_image_labels for URI {uri}: {labels}')
    return labels


def event_received(setup: Setup, producer: SerializingProducer, event_key: str, event_val: dict):
    event_handler_func = setup.event_handlers[event_val['action']]
    event_handler_func(setup, producer, event_key, event_val)


def event_handler_add_image(setup: Setup, producer: SerializingProducer, event_key: str, event_val: dict):
    payload = event_val['payload']
    if not setup.redis_tbl_name or not event_key or not payload:
        raise Exception('redis_tbl_name, event_key or payload not set')
    rds_key = f'{setup.redis_tbl_name}:{event_key}'
    # setup.redis_client.delete(rds_key)
    # print(f'event_handler_add_image => {event_key}-> {payload}')
    redis_service.put_map_if_missing(
        setup.redis_client,
        rds_key,
        lambda rec_id: detect_image_labels(setup, payload),
        lambda key, labels: print(f'Added image-labels for key={key}: {labels}'),
        lambda k: print(f'Key {k} already exists'))

    # Add the same record again but this time as key/JSon pair for easy spark-redis consumption
    redis_service.put_map(
        setup.redis_client,
        f'{setup.redis_json_tbl_name}:{event_key}',
        {f'picture_id': event_key, f'uri': payload, f'labels': get_record_as_json(setup, rds_key)})

    if producer is not None:
        event_producer.produce_event(producer, setup.topic, event_key, event_val)


def get_record_as_json(setup, rec_id):
    m = redis_service.get_map(setup.redis_client, rec_id)
    j = json.dumps(m)
    print(f'{rec_id} ::: {j}')
    return j

def process(s: Setup):
    continue_consuming = lambda i: eval(s.continue_consuming_str, {"index": i})
    producer = event_producer.init(s.kafka_config, s.topic)
    event_consumer.start_consuming(
        create_streaming_consumer(s.kafka_config, s.topic, s.offset),
        lambda key, val: event_received(s, producer, key, val),
        continue_consuming)


if __name__ == '__main__':
    conf, topic, continue_consuming_str = event_consumer.read_args_consumer()
    print(f'img_label_processor.py args: conf={conf}, topic={topic}, continue_consuming_str={continue_consuming_str}')
    process_setup = Setup(
        redis_service.create_redis_client(),
        create_vision_client(),
        get_pexel_token(),
        conf,
        topic,
        continue_consuming_str,
        {"AddImage": event_handler_add_image},
        # offset => 'earliest' 'latest' 'beginning'
        'beginning',
        'ImageLabels',
        'ImageLabelsJson')
    process(process_setup)


