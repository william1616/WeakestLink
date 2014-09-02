from distutils.core import setup
from glob import glob
import py2exe, sys    

sys.path.extend(['.', './/weakest_link'])

buildOptions = {'optimize': 2,
                'bundle_files': 2,
                }
                
dataFiles = [('resources', glob('./resources/*')),
             ('.', ['./config.json'])
			 ]

setup(windows=['main.py'], 
      options={'py2exe': buildOptions},
      data_files=dataFiles,
	  zipfile=None
	  )
