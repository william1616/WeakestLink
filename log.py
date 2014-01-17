from datetime import datetime
from json import load, dump
from os.path import basename
import __main__

def initConfig():    
    #config settings
    fileName = 'config.json'
    options = {"Tk": {"window_title": "The Weakest Link", "status_lines": 25}, "questions": {"mainQ": "questions.csv", "finalQ": "questions.csv"}, "server": {"bindPort": 1024, "bindAddress": "localhost"}, "debug": {"fileName": "log.txt", "log": True}}
    
    with open(fileName, 'r') as configFile:
        try:
            config = load(configFile)
            if not isinstance(config, dict):
                print('ConfigFile is not a Dictionary')
                raise
            for key in options:
                value = options.get(key)
                if key in config:
                    for subkey in value:
                        subvalue = value.get(subkey)
                        if not subkey in config[key]:
                            print('cannot find key [' + key + '][' + subkey + ' in ConfigFile')
                            raise
                else:
                    print('cannot find key [' + key + '] in ConfigFile')
                    raise
                return config
        except:
            print('Overwritting config file')
            with open(fileName, 'w') as configFile:
                dump(options, configFile, indent=4)
            return options

config = initConfig()
logName = basename(__file__)

def log(text, fileName=config['debug']['fileName']):
    if config['debug']['log']:
        with open(fileName, 'a') as file:
            file.write(str(datetime.now()) + ' [' + logName + '] ' + text + '\n')
