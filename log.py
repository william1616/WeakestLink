from datetime import datetime
from json import load
from os.path import basename

def initConfig():    
    #config settings
    fileName = 'config.json'
    options = {"Tk": {"window_title": "The Weakest Link", "status_lines": 25}, "questions": {"mainQ": "questions.csv", "finalQ": "questions.csv"}, "server": {"bindPort": 1024, "bindAddress": "localhost"}, "debug": {"fileName": "log.txt", "log": True}}
    
    with open(fileName, 'r') as configFile:
        config = load(configFile)
        if not isinstance(config, dict):
            raise KeyError('ConfigFile is not a dictionary')
        for key in config.values():
            print(str(key))
            print(str(type(key)))
            if isinstance(key, dict):
                for subkey in key.values():
                    if not isinstance(subkey, str) or not subkey in options[key]:
                        raise KeyError('Key [' + str(key) + '][' + str(subkey) +'] not found in configFile')
            elif isinstance(key, str):
                if not isinstance(key, str) or not key in options[key]:
                    raise KeyError('Key [' + str(key) + '] not found in configFile')
        return config

config = initConfig()

def log(text, fileName=config['debug']['fileName']):
    if config['debug']['log']:
        with open(fileName, 'a') as file:
            file.write(str(datetime.daynow()) + ' [' + basename(__file__) + '] ' + text + '\n')
