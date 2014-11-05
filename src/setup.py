from distutils.core import setup
from glob import glob
import py2exe, sys, datetime, json, os

#open the json config file containg the build name/number
with open('..//build//buildData.json', 'r') as file:
  buildData = json.load(file) #load the json to a python dict

if input('Release Build [n]: ').lower() == 'y': #if the build is a release build
  temp = input('Version: [' + str(buildData['version']) + ']: ') #ask for a new version name
  if temp: buildData['version'] = temp #use the old version name is no version name given
  versionName = 'Build ' + str(buildData['buildNo']) + ' [' + buildData['version'] + ']' #set the versionName to the build number and version specified in the config

  #version is of the form x-Alpha.y
  versionList = buildData['version'].split('.') #split the version into its components
  newVersionEnd = str(int(versionList[len(versionList) - 1]) + 1) #get the last component (in this case y) and increment it
  newVersion = '.'.join(versionList[:len(versionList) - 1]) # get the rest of the version => i.e x-Alpha
  newVersion = newVersion + '.' + newVersionEnd #add the new last component onto the version x-Alpha.(y+1)

  buildData['version'] = newVersion #set the value in the config to the new value
else: #otherwise if the build is not a release build
  versionName = 'Build ' + str(buildData['buildNo']) #set the versionName to the value in the config file

buildData['buildNo'] += 1 #increment the build number

#open the config file
with open('..//build//buildData.json', 'w') as file:
  json.dump(buildData, file, indent=4) #save the new build number/version to the config file

buildOptions = {'optimize': 2, #extra optimization 
                'bundle_files': 3, #don't bundle files
                'dist_dir': '..//build//' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + ' ' + versionName, #use a directory in /build which has a name equivilant to the current timestamp and the versionName
                }
        
dataFiles = [('resources', glob('./resources/*')), #copy all the files in src/resources to /build/{buildFolder}/resources/
             ('.', ['./config.json']) #copy the config file to /build/{buildFolder}/
            ]
       
setup(windows=['main.py'], #the window applicaton is main.py
      console=[], #there are no console applications
      options={'py2exe': buildOptions}, #get the options dict
      data_files=dataFiles, #get the list of data files
      zipfile=None #don't create a shared zip folder instead bundle the files as part of the exe
     )