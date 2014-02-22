from cx_Freeze import setup, Executable
import sys, datetime, json, os

with open('build\\buildData.json', 'r') as file:
    buildData = json.load(file)

if input('Release Build [n]: ') == 'y':
    temp = input('Version: [' + str(buildData['version']) + ']: ')
    if temp: buildData['version'] = temp
    versionName = 'Build ' + str(buildData['buildNo']) + ' [' + buildData['version'] + ']'

    versionList = buildData['version'].split('.')
    newVersionEnd = str(int(versionList[len(versionList) - 1]) + 1)
    newVersion = '.'.join(versionList[:len(versionList) - 1])
    newVersion = newVersion + '.' + newVersionEnd + '-Alpha'

    buildData['version'] = newVersion
else:
    versionName = 'Build ' + str(buildData['buildNo'])

buildData['buildNo'] += 1

with open('build\\buildData.json', 'w') as file:
    json.dump(buildData, file, indent=4)
    
# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = ['network', 'misc', 'control', 'gui', 'server', 'tkinter', 'csv', 'threading', 'time', 'sys', 'json', 'os', 'network', 'datetime', 'math', 'operator', 'pygame', 'collections', 'hashlib'], 
    excludes = [], 
    path = sys.path.extend(os.path.dirname(os.path.abspath(__file__))),
    include_files = [('config.json',''), ('questions.csv',''), ('redPlaceholder.png',''), ('bluePlaceholder.png','')],
    create_shared_zip = True,
    compressed = True,
    build_exe = 'build\\' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + ' ' + versionName)

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('main.py', 
    base=base, 
    targetName = 'The Weakest Link.exe')
]

setup(name='The Weakest Link',
      version = versionName,
      description = 'The Weakest Link Game',
      options = dict(build_exe = buildOptions),
      executables = executables)
