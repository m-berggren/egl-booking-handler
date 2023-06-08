import yaml
import json


with open(f'app\eglhandler\config.yaml', 'r') as f:
    data = yaml.safe_load(f)

with open(f'app\eglhandler\config.json', 'w') as f:
    json.dump(data, f, indent=4)