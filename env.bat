@ECHO OFF
SET AMPADB_SETTINGS=%cd%\debug.ini
IF EXIST "private.ini" (
  SET AMPADB_SETTINGS=%AMPADB_SETTINGS%;%cd%\private.ini
)

IF NOT EXIST "venv" (
  ECHO No existeix l'entorn virtual. Ara es crearà.
  virtualenv --system-site-packages venv
  REM Assumeix que Virtualenv és per a Python 3, a falta d'una solució millor
  IF NOT ERRORLEVEL 0 (
    REM virtualenv ha fallat
    ECHO virtualenv no està instalat o ha fallat
    EXIT /B 1
  )
  venv\Scripts\activate
  pip install "setuptools>=18.5"
  pip install -r stdrequirements.txt
) ELSE (
  venv\Scripts\activate
)
