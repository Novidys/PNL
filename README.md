# Introduction
      ______                     _   _                 _                _    
      | ___ \                   | \ | |               | |              | |   
      | |_/ /_ _ _ __ ___  ___  |  \| | _____      __ | |     ___  __ _| | __
      |  __/ _` | '__/ __|/ _ \ | . ` |/ _ \ \ /\ / / | |    / _ \/ _` | |/ /
      | | | (_| | |  \__ \  __/ | |\  |  __/\ V  V /  | |___|  __/ (_| |   < 
      \_|  \__,_|_|  |___/\___| \_| \_/\___| \_/\_/   \_____/\___|\__,_|_|\_\
                                                                       
This script is an attempt to parse leak files and send extracted credentials to a Redis channel.

# How to launch
```
usage: pnl [-h] -c CHANNEL [-H HOST] [-P PORT] [-D] -d DIRECTORY [-w WORKER]
           -e {noext,txt,zip} [{noext,txt,zip} ...]

Leak parser written in Python

optional arguments:
  -h, --help            show this help message and exit
  -c CHANNEL, --channel CHANNEL
                        Redis channel to write to
  -H HOST, --host HOST  Redis host to connect to
  -P PORT, --port PORT  Redis port to connect to
  -D, --debug           Launch the command in debug mode
  -d DIRECTORY, --directory DIRECTORY
                        Directory to analyze
  -w WORKER, --worker WORKER
                        Number of workers to create
  -e {noext,txt,zip} [{noext,txt,zip} ...], --extensions {noext,txt,zip} [{noext,txt,zip} ...]
                        File extensions to parse
``