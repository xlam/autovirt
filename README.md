
# Autovirt

Autovirt is an automatization tool for online turn-based economic game [Virtonomica](https://virtonomica.ru/).
It uses the game API to communicate with the server. There is no any web-scraping doing by Autovirt.

## Features

- automatic equipment repair
- automatic salary raise for units on which minimum employee level does not met
- automatic salary raise for units on which labor union requires raise
- automatic units artefacts renewal
- configurable with python file (to be changed in the future)

## Requirements

- [Python 3.9](https://www.python.org/downloads/release/python-398/)

Autovirt is being developed and tested with Python 3.9. Lower versions are not compatible due to lacking built-in collections type-hinting.

- [Poetry](https://python-poetry.org/) dependency manager

## Installation

1. Clone the repository and step into its directory:
```
$ git clone https://github.com/xlam/autovirt
$ cd autovirt
```
2. Install Autovirt into virtual environment with Poetry. For the first run it will create a new virtual environment and install needed dependencies and Autovirt into it. Provide ``--no-dev`` option to tell poetry not to insall development dependencies:
```
$ poetry install --no-dev
```

## Usage

Start poetry shell to run Autovirt commands:
```
$ poetry shell
```
To exit poetry shell type ``exit`` in terminal. Also it is possible to run single command without invoking shell:
```
$ poetry run python --version
```

After the poetry shell has started python interpreter will be invoked from newly created virtual environment, so we can run the following Autovirt commands:

- repair
- salary
- employee
- innovations

These commands are to be run with ``main.py`` entry point script.
To repair all equipment (as specified in configuration) run the following command:
```
$ python main.py repair -c comp
```
This will repair all computers on all offices (and other units using computers as equipment) provided that "comp" is present in configuration file.

Raise salary at units where minimum qualification does not met:
```
$ python main.py salary 
```

Raise salary at units on which labor union is requiring raise. For this to work there must be mail message from labor union in the game mail inbox:
```
$ python main.py employee
```

Renew innovations (artefacts) on units. For this to work there must be innovation expiration message in the game mail inbox.
```
$ python main.py innovations
```



## Configuration

Copy provided ``config.py.dist`` to ``config.py``, then fill it up with your data.

config.py example:
```
import enum

session_file = 'session.dat'	# file to store logged session
session_timeout = 60 * 30		# lifetime of stored session in seconds
login = ''						# your Virtonomica login
password = ''					# your Virtonomica password
company_id = -1					# your Virtonomica company id (look it up in browser url)

log_dir = 'logs'				# directory to store logs
pagesize = 1000					# maximum returned item (i.e. units) per page

# don't touch this
class Option(enum.Enum):
    equip_id = enum.auto()
    exclude = enum.auto()
    include = enum.auto()
    offer_id = enum.auto()
    quality = enum.auto()


# sample repair configuration
repair = {
    "comp": {  					# configuration name to pass to main.py with --config option
        Option.equip_id: 1515,  # id of equipment to repair
        Option.exclude: [-1],  	# list of units ids to exclude from repair
        Option.offer_id: -1,  	# use this offer id to repair equipment (i.e self offer)
    },
    "comp-hitech": {
        Option.equip_id: 1515,
        Option.include: [-1],  	# list of units ids to repair (only those will be repaired)
        Option.quality: True,  	# repair by installed quality (not required)
    },
    "mtools": {
    	Option.equip_id: 1529   # machine tools
    },
    "drill": {
    	Option.equip_id: 12097  # rock drills
    },
    "tractor": {
    	Option.equip_id: 1530   # tractors
    },
}
```

## Using Autovirt with crontab

Crontab configuration is dependent on the operating system being used. The following configuration is an example for debian/ubuntu servers (need ``. ~/.profile`` to have poetry on system $PATH for crontab):

```
0 9 * * * . ~/.profile && cd ~/autovirt && poetry run python main.py repair -c comp
1 9 * * * . ~/.profile && cd ~/autovirt && poetry run python main.py repair -c comp-hitech
2 9 * * * . ~/.profile && cd ~/autovirt && poetry run python main.py repair -c mtools
3 9 * * * . ~/.profile && cd ~/autovirt && poetry run python main.py repair -c drill
4 9 * * * . ~/.profile && cd ~/autovirt && poetry run python main.py repair -c tractor

5 9 * * * . ~/.profile && cd ~/autovirt && poetry run python main.py innovations

10 9 */2 * * . ~/.profile && cd ~/autovirt && poetry run python main.py employee

15 9 */4 * * . ~/.profile && cd ~/autovirt && poetry run python main.py salary

```