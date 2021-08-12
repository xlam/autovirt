#!/bin/bash

# autovirt dispatcher

echo ""
echo "Activating environment..."
source ./env/bin/activate
echo "Using python executable: $(which python)"

if [ -n "$1" ]
then
  SCRIPT="${1}.py"
  if [ -f "$SCRIPT" ]
    then
      echo "Running script: ${SCRIPT} ${*:2}"
      python "$SCRIPT" "${@:2}"
      wait $!
    else
      echo "Script \"${SCRIPT}\" not found!"
  fi
else
  echo "No parameters found, exiting."
fi

deactivate
