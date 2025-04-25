
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

- [Python 3.13](https://www.python.org/downloads/release/python-3132/) or later

Autovirt developing had been started with Python 3.9 but now Python 3.13 is used. Versions lower than 3.9 are not compatible due to lacking built-in collections type-hinting.

- [uv](https://docs.astral.sh/uv/) dependency manager

## Installation

### Using git and poetry

1. Clone the repository and step into its directory:
```
$ git clone https://github.com/xlam/autovirt
$ cd autovirt
```
2. Install Autovirt into virtual environment with uv. For the first run it will create a new virtual environment and install needed dependencies and Autovirt into it. Provide ``--no-dev`` option to tell poetry not to insall development dependencies:
```
$ uv sync --no-dev
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

After the poetry shell has started, python interpreter and installed ``autovirt`` command will be invoked from newly created virtual environment, so we should be able now to run autovirt the same way as with pip installation.

See ``autovirt --help`` to figure out available actions.

Use ``--dry-run`` option to tell autovirt not to apply changes, just show them.

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
```

## Using Autovirt with crontab

Crontab configuration is dependent on the operating system being used. The following configuration is an example for debian/ubuntu servers (need ``. ~/.profile`` to have poetry on system $PATH for crontab):

```
0 9 * * * . ~/.profile && cd ~/autovirt && poetry run autovirt equipment repair-with-offer 1515 -o [offer_id] -e [units_ids_to_exclude] 
1 9 * * * . ~/.profile && cd ~/autovirt && poetry run autovirt equipment repair 1515 -u [units_ids_to_repair_only] -k 
2 9 * * * . ~/.profile && cd ~/autovirt && poetry run autovirt equipment repair 1529

5 9 * * * . ~/.profile && cd ~/autovirt && poetry run autovirt artefact renew

10 9 */2 * * . ~/.profile && cd ~/autovirt && poetry run autovirt employee set-required-salary
15 9 */4 * * . ~/.profile && cd ~/autovirt && poetry run autovirt employee set-demanded-salary

11 9 */2 * * . ~/.profile && cd ~/autovirt && poetry run autovirt logistics optimize-shops-supplies

11 9 */2 * * . ~/.profile && cd ~/autovirt && poetry run autovirt sales manage-retail-prices [shop_id]
```
