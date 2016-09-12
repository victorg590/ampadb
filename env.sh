#!/bin/sh
# Arxiu que defineix l'entorn per a proves
# Utilitzar com
#   . env.sh

# Utilitza la configuració a l'arxiu "debug.ini"
export AMPADB_SETTINGS="$(pwd)/debug.ini"
if [ -f "private.ini" ]; then
  AMPADB_SETTINGS="$AMPADB_CONFIG:$(pwd)/private.ini"
fi
if [ ! -d "venv" ]; then
  echo "No existeix l'entorn virtual. Ara es crearà."
  virtualenv3 --system-site-packages "venv"
  if [ $? != 0 ]; then
    # virtualenv ha fallat
    echo "virtualenv no està instalat o ha fallat."
    return 1
  fi
  . venv/bin/activate
  pip3 install 'setuptools>=18.5'
  pip3 install -r stdrequirements.txt
else
  . venv/bin/activate
fi
