import json


def wei_to_ether(wei):
    return wei / (10 ** 18)

def open_file(file):
    with open(file, "r") as f:
        return json.load(f)
