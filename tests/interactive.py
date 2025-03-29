from worker_object_server.object_server import ObjectServer
import json

with open('tests/worker_parameters_config.json', 'r') as f:
    config = json.load(f)

obj = ObjectServer(config)

def end():
    obj.stop()
    exit()
