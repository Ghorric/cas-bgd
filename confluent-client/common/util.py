import argparse
import ast


def required_args_specification(required):
    required.add_argument('-f',
                          dest="config_file",
                          help="path to configuration file",
                          required=True,
                          type=ast.literal_eval)
    required.add_argument('-t',
                          dest="topic",
                          help="topic name",
                          required=True,
                          type=ast.literal_eval)
    required.add_argument('-c',
                          dest="continue_consuming",
                          help="Continue consuming events as long as evaluated str returns True (e.g., '-c index<1')",
                          required=False,
                          default='"True"',
                          type=ast.literal_eval)


def parse_args(specification=required_args_specification):
    parser = argparse.ArgumentParser(
             description="Arguments for apps built on top of confluent-client")
    parser._action_groups.pop()
    required = parser.add_argument_group('required arguments')
    specification(required)
    args, unknown = parser.parse_known_args()
    return args


def read_kafka_config_file(config_file):
    config = {}
    with open(config_file) as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                config[parameter] = value.strip()
    return config