#!/bin/bash

# autovirt dispatcher

SCRIPT="main.py"

function log() {
    echo "$(date "+%Y-%m-%d %T"): $1"
}

echo ""
log "Activating environment..."
source ./env/bin/activate
log "Using python executable: $(which python)"

if [ -n "$1" ]
then
  if [ -f "$SCRIPT" ]
    then
      log "Running script: ${SCRIPT} ${*:1}"
      python "$SCRIPT" "${@:1}"
      wait $!
    else
      log "Script \"${SCRIPT}\" not found!"
  fi
else
  log "No parameters found, exiting."
fi

deactivate
