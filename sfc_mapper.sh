#!/usr/bin/env bash
set -e

INPUT_FILE=""
CURRENT_DIR=$(cd -P -- "$(dirname -- "$0")" && pwd -P)

if [ ! -z "$1" ];
  then
    INPUT_FILE=`echo "$1"`
    echo "Parsing input file: $INPUT_FILE"
  else
    echo "missing input file param"
    exit 1
fi

#Install pandas package
if ! (pip freeze | grep pandas) > /dev/null; then
  echo "Installing pandas"
  pip install pandas
fi


python sfc_mapper.py $CURRENT_DIR/$INPUT_FILE

STATUS=$?
if [ $STATUS -eq 0 ]
   then
      echo "Finished processing input file successfully." $?
   else
      echo "Error happened while processing input file." $?
fi
exit $STATUS