
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

### Using git and poetry
1. Clone the repository and step into its directory:
```
$ git clone https://github.com/xlam/autovirt
$ cd autovirt
```
2. Install Autovirt into virtual environment with Poetry. For the first run it will create a new virtual environment and install needed dependencies and Autovirt into it. Provide ``--no-dev`` option to tell poetry not to insall development dependencies:
```
$ poetry install --no-dev
```

### Using wheel
1. Download latest wheel package from [https://github.com/xlam/autovirt/releases](https://github.com/xlam/autovirt/releases)
2. Install downloaded wheel with pip:
```
$ pip install autovirt-<version>-py3-none-any.whl
```
In last case you may install autivirt into system python or into any virtual environment of choice.
## Usage
In case autovirt installed with pip you could just use ``autovirt`` entry script:
```
$ autovirt --help
```


In case you installed autovirt via poetry you should start poetry shell:
```
$ poetry shell
```
It is also possible to run single command without invoking the shell:
```
$ poetry run autovirt --help
```
To exit poetry shell type ``exit`` in terminal.

After the poetry shell has started python interpreter and installed ``autovirt`` command will be invoked from newly created virtual environment, so we can run the following Autovirt commands the same way as with pip installation:

- repair
- salary
- employee
- innovations

To repair all equipment (as specified in configuration) run the following command:
```
$ autovirt repair -c comp
```
This will repair all computers on all offices (and other units using computers as equipment) provided that "comp" is present in configuration file.

Raise salary at units where minimum qualification does not match:
```
$ autovirt salary
```

Raise salary at units on which labor union is requiring raise.
```
$ autovirt employee
```

Renew all innovations (artefacts) having time to live lesser then 5. 
```
$ autovirt innovations
```



## Configuration

Copy provided ``autovirt.toml.dist`` to ``autovirt.toml``. The configuration file must present in a directory from which ``autovirt`` command to be executed. Fill the file up with your data.
TOML syntax is very similar to .ini files.

autovirt.toml example (fill empty values with your data):
```
[autovirt]
session_file = "session.dat"
session_timeout = 1800          # 30 minutes
login = ""                      # Virtonomica user login
password = ""                   # Virtonomica user password
company_id =                    # user company id
log_dir = "logs"                # logs directory name
pagesize = 1000                 # number of entries to return in server response

[repair]                        # repair module configuration

    [repair.comp]               # configuration name to pass to main.py with --config option
        equipment_id = 1515     # id of equipment to repair
        exclude = []            # list of units ids to exclude from repair
        offer_id =              # use this offer id to repair equipment (i.e self offer)

    [repair.comp-hitech]
        equipment_id = 1515
        include = []            # list of units ids to repair (only those will be repaired)
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
