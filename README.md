
# Autovirt

Autovirt is an automatization tool for online turn-based economic game [Virtonomica](https://virtonomica.ru/).
It uses the game API to communicate with the server. There is no any web-scraping doing by Autovirt.

## Features

- automatic equipment repair
- automatic salary raise for units on which minimum employee level does not met
- automatic salary raise for units on which labor union requires raise
- automatic units artefacts renewal
- configurable with simple [toml](https://toml.io/en/) configuration file
- bash and zsh autocompletion support

## Requirements

- [Python 3.13](https://www.python.org/downloads/release/python-3132/) or later

Autovirt developing had been started with Python 3.9 but now Python 3.13 is used. Versions lower than 3.9 are not compatible due to lacking built-in collections type-hinting.

- [uv](https://docs.astral.sh/uv/) dependency manager

## Installation

### Using git and uv

1. Clone the repository and step into its directory:
```
$ git clone https://github.com/xlam/autovirt
$ cd autovirt
```
2. Install Autovirt into virtual environment with uv. For the first run it will create a new virtual environment and install needed dependencies and Autovirt into it. Provide ``--no-dev`` option to tell uv not to install development dependencies:
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


In case you installed autovirt via uv you should activate the virtual environment:
```
$ source .venv/bin/activate
```
It is also possible to run single command without activating the environment:
```
$ uv run autovirt --help
```
To exit the activated environment type ``deactivate`` in terminal.

After the virtual environment has been activated, python interpreter and installed ``autovirt`` command will be invoked from the virtual environment, so we should be able now to run autovirt the same way as with pip installation.

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
base_url = "https://virtonomica.ru/api/vera"
login = ""                      # Virtonomica user login
password = ""                   # Virtonomica user password
company_id =                    # user company id
log_dir = "logs"                # logs directory name
pagesize = 1000                 # number of entries to return in server response
_mm_key_ = ""                   # Critical cookie for API access (optional, required for some endpoints)
_mm_user_ = ""                  # Critical cookie for API access (optional, required for some endpoints)
```

**Note**: The critical cookies (`_mm_key_` and `_mm_user_`) need to be obtained by the user, for example through browser developer tools after web login to Virtonomica. These cookies are required for accessing certain API endpoints.

## Using Autovirt with crontab

Crontab configuration is dependent on the operating system being used. The following configuration is an example for debian/ubuntu servers (need to activate uv environment for crontab):

```
0 9 * * * . ~/.profile && cd ~/autovirt && /path/to/uv run autovirt equipment repair-with-offer 1515 -o [offer_id] -e [units_ids_to_exclude]
1 9 * * * . ~/.profile && cd ~/autovirt && /path/to/uv run autovirt equipment repair 1515 -u [units_ids_to_repair_only] -k
2 9 * * * . ~/.profile && cd ~/autovirt && /path/to/uv run autovirt equipment repair 1529

5 9 * * * . ~/.profile && cd ~/autovirt && /path/to/uv run autovirt artefact renew

10 9 */2 * * . ~/.profile && cd ~/autovirt && /path/to/uv run autovirt employee set-required-salary
15 9 */4 * * . ~/.profile && cd ~/autovirt && /path/to/uv run autovirt employee set-demanded-salary

11 9 */2 * * . ~/.profile && cd ~/autovirt && /path/to/uv run autovirt logistics optimize-shops-supplies

11 9 */2 * * . ~/.profile && cd ~/autovirt && /path/to/uv run autovirt sales manage-retail-prices [shop_id]
```

Note: Replace `/path/to/uv` with the actual path to your uv executable.

## Shell Autocompletion

To enable autocompletion for autovirt commands, you can use the provided completion scripts for both bash and zsh.

### For Bash

1. Source the completion script in your shell:
```bash
source /path/to/autovirt-completion.bash
```

2. Or copy the completion script to the system-wide bash completion directory:
```bash
sudo cp autovirt-completion.bash /etc/bash_completion.d/
```

3. Or add the following line to your `~/.bashrc` to load it automatically:
```bash
source /path/to/autovirt-completion.bash
```

### For Zsh

1. Place the zsh completion file in your zsh completion directory:
```bash
# Usually located at ~/.zsh/completion/ or /usr/local/share/zsh/site-functions/
mkdir -p ~/.zsh/completion/
cp _autovirt ~/.zsh/completion/
# Or
sudo cp _autovirt /usr/local/share/zsh/site-functions/
```

2. Make sure your `~/.zshrc` includes the completion path:
```bash
fpath=(~/.zsh/completion $fpath)
autoload -Uz compinit && compinit
```

After setup, you will be able to use tab completion for autovirt commands, services, and actions.
