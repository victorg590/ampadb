#!/bin/sh
# Arxiu que defineix l'entorn per a proves
# Utilitzar com
#   . env.sh

# Utilitza la configuració a l'arxiu "debug.ini"
export AMPADB_SETTINGS="$(pwd)/debug.ini"
if [ -f "private.ini" ]; then
  AMPADB_SETTINGS="$AMPADB_CONFIG:$(pwd)/private.ini"
fi
if [ ! -d "virtualenv" ]; then
  echo "No existeix l'entorn virtual. Ara es crearà."
  virtualenv3 "virtualenv"
  [ $? != 0 ] && echo "Cal instalar virtualenv per a Python 3" && return
  . virtualenv/bin/activate
  pip install 'setuptools>=18.5'
  pip install -r stdrequirements.txt
else
  . virtualenv/bin/activate
fi
