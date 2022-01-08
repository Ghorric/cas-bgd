import os
import redis
import ast
from redis import StrictRedis
from typing import Callable
import common.util as util

tbl_name_user_id_mapping = 'user-id-mapping'
# tbl_name_user_sim = 'user-similarity'
tbl_name_user_sim = 'user-similarity-euclidean'
tbl_name_img = 'ImageLabels'
tbl_name_img_json = 'ImageLabelsJson'


def create_redis_client() -> StrictRedis:
    redis_host = os.environ.get('REDIS_HOST', 'localhost')
    redis_port = int(os.environ.get('REDIS_PORT', '6379'))
    redis_pw = os.environ.get('REDIS_PASSWORD', 'UNKNOWN')

    # print("{}={}".format('redis_host', redis_host))
    # print("{}={}".format('redis_port', redis_port))
    # print("{}={}".format('redis_pw', redis_pw))
    return redis.StrictRedis(
        host=redis_host,
        port=redis_port,
        password=redis_pw,
        encoding="utf-8",
        decode_responses=True)


def put_map_if_missing(redis_client:StrictRedis,
                       key: str,
                       collect_data_func: Callable[[str], dict],
                       collected_post_processing: Callable[[str, dict], None] = lambda k, v: None,
                       ignore_because_exists_processing: Callable[[str], None] = lambda k: None) -> bool:
    exists = redis_client.exists(key) > 0
    if exists:
        ignore_because_exists_processing(key)
        return False
    collected = collect_data_func(key)
    collected_post_processing(key, collected)
    return put_map(redis_client, key, collected)


def put_map(redis_client:StrictRedis, key: str, mapping: dict) -> bool:
    num_updated = redis_client.hset(key, mapping=mapping)
    return num_updated > 0


def get_map(redis_client:StrictRedis, key: str) -> dict:
    return redis_client.hgetall(key)


def get_image_labels_keys(redis_client:StrictRedis, tbl_name=tbl_name_img) -> []:
    return redis_client.keys(f'{tbl_name}:*')


def get_image_labels(redis_client:StrictRedis, key, tbl_name=tbl_name_img) -> []:
    return get_map(redis_client, f'{tbl_name}:{key}')


def print_image_labels_keys(redis_client:StrictRedis, tbl_name=tbl_name_img):
    keys = get_image_labels_keys(redis_client, tbl_name)
    for k in keys:
        print(f"key -> {k}")
        print(f"            vals -> {get_map(redis_client, k)}")
    print(f"Total '{tbl_name}' entries: {len(keys)}")

def print_user_similarity(redis_client:StrictRedis):
    tbl = tbl_name_user_sim
    keys = redis_client.keys(f'{tbl}:*')
    for k in keys:
        print(f"key -> {k}")
        # redis_client.delete(k)
        print(f"            vals -> {get_map(redis_client, k)}")
    print(f"Total '{tbl}' entries: {len(keys)}")


def search_similar_user(redis_client:StrictRedis, user_name, verbose=False):
    id_mapping = get_map(redis_client, f'{tbl_name_user_id_mapping}:{user_name.replace(" ", "_")}')['user_id']
    if verbose:
        print(f"The UserID for '{user_name}' is: {id_mapping}")
    ids = redis_client.keys(f'{tbl_name_user_sim}:{id_mapping}:*')
    all = []
    for id in ids:
        m = get_map(redis_client, id)
        all.append((m['user2_name'], m['similarity']))
    if verbose:
        print(f"All similarity comparisons for user '{user_name}':")
        for peer in all:
            print(f"\t {peer}")
    if not all:
        return None
    return max(all, key=lambda item: item[1])


def print_search_similar_user(redis_client:StrictRedis, user_name, verbose=False):
    similar = search_similar_user(redis_client, user_name, verbose)
    print(f"A similar user for '{user_name}' is: { None if not similar else similar[0]}")


def args_spec(required):
    required.add_argument('-u',
                          dest="user",
                          help="user name as input for similarity search",
                          required=False,
                          default='"Alexis Bailey"',
                          type=ast.literal_eval)
    required.add_argument('-v', '--verbose', dest="verbose", action='store_true')

if __name__ == '__main__':
    args = util.parse_args(args_spec)
    user = args.user
    verbose = args.verbose
    redis_client = create_redis_client()
    # print(f'{put_map_if_missing(redis_client, "mk1", lambda k: {"k01": "v01"})}')
    # print(f'{get_map(redis_client, "mk1")}')

    # print(f'{get_map(redis_client, "dummy_946337")}')
    # redis_client.delete('dummy')

    # print_image_labels_keys(redis_client)
    # print_image_labels_keys(redis_client, tbl_name_img_json)

    # print_user_similarity(redis_client)
    print_search_similar_user(redis_client, user, verbose)
