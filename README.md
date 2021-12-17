
# Autovirt

Autovirt is an automatization tool for online turn-based economic game [Virtonomica](https://virtonomica.ru/).
It uses the game API to communicate with the server. There is no any web-scraping doing by Autovirt.

## Features

- automatic equipment repair
- automatic salary raise for units on which minimum employee level does not met
- automatic salary raise for units on which labor union requires raise
- automatic units artefacts renewal
- configurable with simple [toml](https://toml.io/en/) configuration file

## Requirements

- [Python 3.9](https://www.python.org/downloads/release/python-398/) or later

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
To exit poetry shell type ``exit`` in terminal. Also, it is possible to run single command without invoking shell:
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

Raise salary at units where minimum qualification does not match:
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

Copy provided ``autovirt.toml.dist`` to ``autovirt.toml``, then fill it up with your data.
TOML syntax is very similar to .ini files.

autovirt.toml example (fill placeholders with your data):
```
[autovirt]
session_file = "session.dat"
session_timeout = 1800          # 30 minutes
login = ""                      # Virtonomica user login
password = ""                   # Virtonomica user password
company_id = -1                 # user company id
log_dir = "logs"                # logs directory name
pagesize = 1000                 # number of entries to return in server response

[repair]                        # repair module configuration

    [repair.comp]               # configuration name to pass to main.py with --config option
        equipment_id = 1515     # id of equipment to repair
        exclude = [-1]          # list of units ids to exclude from repair
        offer_id = -1           # use this offer id to repair equipment (i.e self offer)

    [repair.comp-hitech]
        equipment_id = 1515
        include = [-1]          # list of units ids to repair (only those will be repaired)
        quality = true          # repair by installed quality (not required)

    [repair.mtools]
        equipment_id = 1529     # machine tools

    [repair.drill]
        equipment_id = 12097    # rock drills

    [repair.tractor]
        equipment_id = 1530     # tractors

    [repair.saw]
        equipment_id = 10717    # sawmill
```

## Using Autovirt with crontab

Crontab configuration is dependent on the operating system being used. The following configuration is an example for debian/ubuntu servers (need ``. ~/.profile`` to have poetry on system $PATH for crontab):

```
0 9 * * * . ~/.profile && cd ~/autovirt && poetry run autovirt repair -c comp
1 9 * * * . ~/.profile && cd ~/autovirt && poetry run autovirt repair -c comp-hitech
2 9 * * * . ~/.profile && cd ~/autovirt && poetry run autovirt repair -c mtools
3 9 * * * . ~/.profile && cd ~/autovirt && poetry run autovirt repair -c drill
4 9 * * * . ~/.profile && cd ~/autovirt && poetry run autovirt repair -c tractor

5 9 * * * . ~/.profile && cd ~/autovirt && poetry run autovirt innovations

10 9 */2 * * . ~/.profile && cd ~/autovirt && poetry run autovirt employee

15 9 */4 * * . ~/.profile && cd ~/autovirt && poetry run autovirt salary

```
