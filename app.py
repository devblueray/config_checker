import time
import re
import yaml
import requests
import os
import json

### GITHUB VARIABLES ####
branch = os.getenv("GITHUB_REF_NAME")
owner = os.getenv("GITHUB_ACTOR")
webhook = os.getenv("INPUT_WEBHOOK")
env_source = os.getenv("ENV_SOURCE")
#########################

def parse_elixir_config():
    elixir_vars = []
    f = open('elixir-config', 'r')
    lines = f.readlines()
    reStr = re.compile("\"(?P<envName>[A-Z_]+([A-Z_][A-Z]+))+\"")
    for l in lines:
        if "fetch_env!" in l:
            r = re.search(reStr, l)
            if r:
                elixir_vars.append(r.group("envName"))
    return elixir_vars

def parse_yaml_config():
    env_config = []
    resp = requests.get(env_source)
    with open("env.yaml", "w") as env_file:
        env_file.write(resp.text)
 
    with open('env.yaml', 'r') as stream:
        try:
            data = yaml.load(stream, Loader=yaml.FullLoader)
            for i in data['shared']['env']:
                env_config.append(i['name'])
        except yaml.YAMLError as e:
            print(e)
    return env_config

def send_to_slack(parameters, branch, creator):
    print(f"Undefined parameters {parameters} on branch {branch} owned by {owner}")
    message = {"text": f"Undefined parameters {parameters} on branch {branch} owned by {owner}"}
    requests.post(webhook, json.dumps(message))

if __name__ == '__main__':
    elixir_config = parse_elixir_config()
    env_config = parse_yaml_config()
    print(env_config)
    if not all(elem in env_config for elem in elixir_config):
        parameters = list(set(elixir_config) - set(env_config))
        send_to_slack(parameters, branch, owner)
