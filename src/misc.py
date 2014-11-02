from datetime import datetime
from json import load, dump
from traceback import extract_stack

#initalise the config
def initConfig(fileName='config.json'):
  #options list here needs to be kept up to date with config fields; it is the default options list for the application
  options = {"Tk": {"window_title": "The Weakest Link", "status_lines": 25}, "questions": {"mainQ": "resources/questions.csv", "finalQ": "resources/questions.csv", "finalRndQCnt": 10, "sortQuestions": False, "contestantCnt": 8}, "server": {"bindPort": 1024, "bindAddress": "localhost"}, "debug": {"fileName": "log.txt", "log": False}, "pygame": {"font": "microsoftsansserif", "window_title": "The Weakest Link", "fps": 10, "width": 800, "height": 600, "fullscreen": False}}
  with open(fileName, 'r') as configFile: #open the configfile for reading
    try:
      config = load(configFile) #load the json from the config file to a local variable
      if not isinstance(config, dict):
        #if the config is not a dictionary overwrite the config file
        print('ConfigFile is not a Dictionary')
        raise #break out of the try and go to the first except stmnt by raising a generic error
      for key, value in options.items(): #for each key and value in options
        if key in config: #check if the key is in the config file
          if isinstance(value, dict): #if the value is a dictionary
            for subkey in value: #loop through each subkey in the dictionary
              if not subkey in config[key]: #if the subkey is not in the config overwrite the config file
                print('Cannot find key [' + key + '][' + subkey + '] in ConfigFile')
                raise #break out of the try and go to the first except stmnt by raising a generic error
        else: #if the key is not in the config file overwrite the config file
          print('Cannot find key [' + key + '] in ConfigFile')
          raise #break out of the try and go to the first except stmnt by raising a generic error
      return config #return the config => this will only happen if no errors have been thrown upto this point
    except Exception as e: #an error has been thrown => the config file is invalid => overwrite the config file with the default values to prevent errors in the program
      print(e)
      print('Overwritting config file')
      writeConfig(options, fileName) #write the default options to the config file
      return options #return the default options

#write the config dict to file
def writeConfig(config, fileName='config.json'):
  with open(fileName, 'w') as configFile: #open the file with write permisions => if the file doesn't exist create it
    dump(config, configFile, indent=4) #dump the dict into the file as a json formated with an indent of 4 spaces
      
#load the config from file
config = initConfig()

#log a message to file
def log(text, forceLog=False, fileName=config['debug']['fileName']):
  logName = extract_stack()[0][0] #get the name of the file calling the log function
  if config['debug']['log'] or forceLog: #if the log is turned on or the function is called with the force argument
    #log the text to file
    with open(fileName, 'a') as file: #open the file in append mode create the file if it does not exist
      file.write(str(datetime.now()) + ' [' + logName + '] ' + text + '\n') #write the current date, file calling the function and log message to the end of the file