REM Arxiu que defineix l'entorn per a proves (Windows CMD)
REM Utilitza la configuració de l'arxiu "debug.ini"

@ECHO OFF
SET AMPADB_SETTINGS=%cd%\debug.ini
IF EXIST "private.ini" (
  SET AMPADB_SETTINGS=%AMPADB_SETTINGS%;%cd%\private.ini
)

IF NOT EXIST "venv" (
  ECHO No existeix l'entorn virtual. Ara es crearà.
  FOR /F "tokens=*" %%i IN ('py -3 -c "import sys; print(sys.executable)"') DO (
    SET PYTHON_EXECUTABLE=%%i
  )
  IF [%PYTHON_EXECUTABLE%] == [] (
    ECHO Es necessita Python 3 per a la instalació
    EXIT /B 1
  )
  virtualenv ^
    --prompt "(ampadb) " ^
    --python %PYTHON_EXECUTABLE% ^
    venv
  IF NOT ERRORLEVEL 0 (
    ECHO virtualenv no està instalat o ha fallat
    EXIT /B 1
  )
  venv\Scripts\activate.bat
  pip install -U "setuptools>=18.5"
  pip3 install -r "requirements.txt" -r "devrequirements.txt"
) ELSE (
  venv\Scripts\activate
)
