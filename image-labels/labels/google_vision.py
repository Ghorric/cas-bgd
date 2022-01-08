import os
import ast
import requests
from google.oauth2 import service_account
from google.cloud import vision

import common.util as util


def create_client(path_gce_credentials) -> vision.ImageAnnotatorClient:
    credentials = service_account.Credentials.from_service_account_file(path_gce_credentials)
    return vision.ImageAnnotatorClient(credentials=credentials)


def required_args_specification(required):
    required.add_argument('-v',
                          dest="vision_config",
                          help="path to vision config file",
                          required=True,
                          type=ast.literal_eval)


def parse_args():
    return util.parse_args(required_args_specification)


def vision_resp_to_dict(vision_resp):
    descriptions = []
    scores = []
    for label in vision_resp:
        descriptions.append(label.description)
        scores.append(label.score)
    return dict(zip(descriptions, scores))


def pexel_request(uri, token):
    resp = requests.get(uri, headers={"Authorization": token})
    return resp.content


def detect_labels(client, content):
    response = client.label_detection({'content': content})
    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    return vision_resp_to_dict(response.label_annotations)


if __name__ == '__main__':
    vision_secret_path = parse_args().vision_config
    pexel_token = os.environ.get('PEXEL_TOKEN', 'UNKNOWN')
    print(f'vision_secret_path: {vision_secret_path}, pexel_token={pexel_token}')
    client = create_client(vision_secret_path)

    uri = 'https://images.pexels.com/photos/7046004/pexels-photo-7046004.jpeg'
    labels = detect_labels(client, pexel_request(uri, pexel_token))
    print(f'dic =>/n{labels}')

