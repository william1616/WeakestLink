from datetime import datetime
from json import load, dump
import os.path
import __main__, threading

class threadFunc(threading.Thread):
    def __init__(self, function): #use lambda to pass args
        theading.Thread.__init__()
        self.function = function
        self.end = False
    def run(self):
        while not self.end:
            self.function()
    def join(self):
        self.end = True
        threading.Thread.join()

def initConfig(fileName=os.path.join(os.path.dirname(__file__), '..\\config.json')):
    #options list here needs to be kept up to date with config fields
    options = {"Tk": {"window_title": "The Weakest Link", "status_lines": 25}, "questions": {"mainQ": "resources/questions.csv", "finalQ": "resources/questions.csv", "finalRndQCnt": 10, "sortQuestions": False}, "server": {"bindPort": 1024, "bindAddress": "localhost"}, "debug": {"fileName": "log.txt", "log": False}, "pygame": {"font": "microsoftsansserif", "window_title": "The Weakest Link", "fps": 10, "width": 800, "height": 600}}
    
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
                        if not subkey in config[key]:
                            print('Cannot find key [' + key + '][' + subkey + '] in ConfigFile')
                            raise
                else:
                    print('Cannot find key [' + key + '] in ConfigFile')
                    raise
            return config
        except:
            print('Overwritting config file')
            writeConfig(options, fileName)
            return options

def writeConfig(config, fileName=os.path.join(os.path.dirname(__file__), '..\\config.json')):
    with open(fileName, 'w') as configFile:
        dump(config, configFile, indent=4)
            
config = initConfig()

def log(text, forceLog=False, fileName=os.path.join(os.path.dirname(__file__), '..//', config['debug']['fileName'])):
    logName = os.path.basename(__file__)
    if config['debug']['log'] or forceLog:
        with open(fileName, 'a') as file:
            file.write(str(datetime.now()) + ' [' + logName + '] ' + text + '\n')
