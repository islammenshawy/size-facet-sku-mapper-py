#!/usr/bin/env bash
set -e

INPUT_FILE=""
CURRENT_DIR=$(cd -P -- "$(dirname -- "$0")" && pwd -P)
CURRENT_BRAND="ON"

if [ ! -z "$1" ] && [ ! -z "$2" ];
  then
    INPUT_FILE=`echo "$1"`
    CURRENT_BRAND=`echo "$2"`
    echo "Parsing input file: $INPUT_FILE for brand: $CURRENT_BRAND"
elif [ ! -z "$1" ] && [ -z "$2" ];
  then
    INPUT_FILE=`echo "$1"`
    echo "Parsing input file: $INPUT_FILE for brand: $CURRENT_BRAND"
else
    echo "missing input file param"
    exit 1
fi

#Install pandas package
if ! (pip freeze | grep pandas) > /dev/null; then
  echo "Installing pandas"
  pip install pandas
fi


python sfc_mapper.py $CURRENT_DIR/$INPUT_FILE $CURRENT_BRAND

STATUS=$?
if [ $STATUS -eq 0 ]
   then
      echo "Finished processing input file successfully." $?
   else
      echo "Error happened while processing input file." $?
fi
exit $STATUS