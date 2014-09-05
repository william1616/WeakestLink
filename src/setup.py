from distutils.core import setup
from glob import glob
import py2exe, sys, datetime, json, os

with open('..//build//buildData.json', 'r') as file:
    buildData = json.load(file)

if input('Release Build [n]: ').lower() == 'y':
    temp = input('Version: [' + str(buildData['version']) + ']: ')
    if temp: buildData['version'] = temp
    versionName = 'Build ' + str(buildData['buildNo']) + ' [' + buildData['version'] + ']'

    versionList = buildData['version'].split('.')
    newVersionEnd = str(int(versionList[len(versionList) - 1]) + 1)
    newVersion = '.'.join(versionList[:len(versionList) - 1])
    newVersion = newVersion + '.' + newVersionEnd

    buildData['version'] = newVersion
else:
    versionName = 'Build ' + str(buildData['buildNo'])

buildData['buildNo'] += 1

with open('..//build//buildData.json', 'w') as file:
    json.dump(buildData, file, indent=4)

buildOptions = {'optimize': 2,
                'bundle_files': 3,
                'dist_dir': '..//build//' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + ' ' + versionName,
                }
                
dataFiles = [('resources', glob('./resources/*')),
             ('.', ['./config.json'])
             ]

setup(windows=['main.py'],
      console=[],
      options={'py2exe': buildOptions},
      data_files=dataFiles,
      zipfile=None
      )
