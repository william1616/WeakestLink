from datetime import datetime
from json import load, dump
from traceback import extract_stack

#compare two python variables
#base => any python variable
#new => variable to compare base against
#checkDictVals => check if the values of dict variables which are not dict variables themselves match ie only check dict keys but do it recursivley
def compareVars(base, new, checkDictVals=True):
  if type(base) != type(new): return False
  if isinstance(base, dict): #if the base is a dict
    for (baseKey, baseValue), (newKey, newValue) in zip(sorted(base.items()), sorted(new.items())): #iterate through the key, value pairs in both the base and the new dicts
      if not compareVars(baseKey, newKey) or not compareVars(baseValue, newValue, checkDictVals): return False #compare the two lists of keys checking the vals then compare the two lists of vals only checking any dict vals if specified by the checkDictVars parameter; if the two variables are not the same return False
  else: #if the base is not a dict
    if checkDictVals: #if checking vals
      return base == new #compare the base and new variables
    else: #otherwise in not checking vals
      return True #return that the vals are equal
  return True #if return false has not yet been executed the two variables must match so return True

#initalise the config
def initConfig(fileName='config.json'):
  #options list here needs to be kept up to date with config fields; it is the default options list for the application
  options = {"Tk": {"window_title": "The Weakest Link", "status_lines": 25}, "questions": {"mainQ": "resources/questions.csv", "finalQ": "resources/questions.csv", "finalRndQCnt": 10, "sortQuestions": False, "contestantCnt": 8}, "server": {"bindPort": 1024, "bindAddress": "localhost"}, "debug": {"fileName": "log.txt", "log": False}, "pygame": {"font": "microsoftsansserif", "window_title": "The Weakest Link", "fps": 10, "width": 800, "height": 600, "fullscreen": False}}
  with open(fileName, 'r') as configFile: #open the configfile for reading
    try:
      config = load(configFile) #load the json file into a dict var
      if not compareVars(options, config, False):
        #check if all the keys in the default options are present in the config from the config file if they are not overwrite the config file by raising an error and going to the first Except statement
        raise ValueError("Invalid Config File")
      else:
        return config
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