import json

# -c 参数指定的file必须是json配置文件

def read_config():
    with open(r"./config.json") as json_file:
        config= json.load(json_file)
    return config

config = read_config()

globals().update(config)

print(nic)
print(instances)