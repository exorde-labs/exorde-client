import os
import yaml


def load_yaml(path) -> dict:
    with open(path, "r") as _file:
        yaml_data = yaml.safe_load(_file)
        return yaml_data


def get_protocol_configuration() -> dict:
    return load_yaml(
        os.path.dirname(os.path.abspath(__file__))
        + "/protocol-configuration.yaml"
    )
