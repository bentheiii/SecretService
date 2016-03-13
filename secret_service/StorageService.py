import json
def to_storage(dictionary):
    return json.dumps(dictionary, separators=(',', ':'))

def from_storage(string):
    return json.loads(string)