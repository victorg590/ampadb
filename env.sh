#!/bin/sh
# Arxiu que defineix l'entorn per a proves
# Utilitzar com
#   source env.sh
# o
#   . env.sh

# Utilitza la configuració a l'arxiu "debug.ini"
export AMPADB_SETTINGS="$(pwd)/debug.ini"
if [ -f "private.ini" ]; then
  AMPADB_SETTINGS="$AMPADB_CONFIG:$(pwd)/private.ini"
fi
