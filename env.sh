#!/bin/sh
# Arxiu que defineix l'entorn per a proves (OS X / Linux / *NIX)
# Utilitza la configuració a l'arxiu "debug.ini"
# Utilitzar com
#   . env.sh
export AMPADB_SETTINGS="$(pwd)/debug.ini"
if [ -f "private.ini" ]; then
  AMPADB_SETTINGS="$AMPADB_SETTINGS:$(pwd)/private.ini"
fi
if [ ! -d "venv" ]; then
  echo "No existeix l'entorn virtual. Ara es crearà."
  PYTHON_EXECUTABLE=$(python3 -c "import sys; print(sys.executable)")
  if [ ! "$PYTHON_EXECUTABLE" ]; then
    echo "Es necessita Python 3 per a la instalació"
    return 1
  fi
  virtualenv \
    --system-site-packages \
    --prompt "(ampadb) " \
    --python "$PYTHON_EXECUTABLE" \
    "venv"
  if [ $? != 0 ]; then
    echo "virtualenv no està instalat o ha fallat."
    return 1
  fi
  . venv/bin/activate
  pip3 install 'setuptools>=18.5'
  pip3 install -r stdrequirements.txt
else
  . venv/bin/activate
fi
