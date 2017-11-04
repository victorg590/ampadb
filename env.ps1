# Arxiu que defineix l'entorn per a proves (Windows CMD)
# Utilitza la configuració de l'arxiu "debug.ini"
$Env:AMPADB_SETTINGS = $PSScriptRoot\debug.ini

$PrivateIni = Test-Path .\private.ini
If ($PrivateIni -eq $True) {
  $Env:AMPADB_SETTINGS = "$Env:AMPADB_SETTINGS`:$PSScriptRoot\private.ini"
}

$Venv = Test-Path .\venv
If ($Venv -eq $False) {
  Write-Output "No existeix l'entorn virtual. Ara es crearà."
  $PythonExecutable = (py -3 -c "import sys; print(sys.executable)")
  If (-Not $PythonExecutable) {
    Write-Output "Es necessita Python 3 per a la instalació"
    Exit 1
  }
  virtualenv `
    --prompt "(ampadb) " `
    --python "$PythonExecutable" `
    "venv"
    If ($? -eq $False) {
      Write-Output "virtualenv no està instalat o ha fallat."
      Exit 1
    }
    Invoke-Expression ".\venv\Scripts\activate.ps1"
    pip install 'setuptools>=18.5'
    pip install -r stdrequirements.txt
} Else {
  Invoke-Expression ".\venv\Scripts\activate.ps1"
}
