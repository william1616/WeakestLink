from cx_Freeze import setup, Executable
import sys, datetime, json, collections

with open('build\\buildData.json', 'r') as file:
	buildData = json.load(file)

if input('Release Build [n]: ') == 'y':
	temp = input('Version: [' + buildData['version'] + ']: ')
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

with open('build\\buildData.json', 'w') as file:
	json.dump(buildData, file, indent=4)
	
# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = ['csv', 'threading', 'time', 'sys', 'json', 'os', 'network', 'datetime'], 
	excludes = ['tk', 'tcl'], 
	path = sys.path, 
	include_files = [('config.json',''), 
	('questions.csv','')],
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
