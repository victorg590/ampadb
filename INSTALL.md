# Windows
Per a Windows, cal instalar diverses dependències abans d'instalar l'aplicació:

* [Python 3][W1]
* [Visual C++ Build Tools][W2]
* [Cairo][W3]
* `lxml` (Veure abaix)
* `virtualenv` (Veure abaix)

Per a instalar `lxml` i `virtualenv`, descarrega el [binari de `lxml`] i
executa aixó on hagis descarregat l'arxiu
`lxml-<versió>-cp<versió Python>-...-win_amd64.whl` (`win32` per a 32-bits),
substituint `lxml.whl` pel nom de l'arxiu (cal iniciar
`cmd.exe` com a administrador):
```bat
pip install lxml.whl virtualenv
```

Després, vés a la carpeta on has descarregat l'aplicació y executa (no cal ser
administrador):
```bat
env.bat
```
Aquest *script* automàticament configurarà les variables necessàries i instalarà
les dependències a un entorn virtual.

# Linux
A Linux, cal instalar les següents dependències amb l'administrador de paquets
de la distribució:

* Python 3
* Compilador de C++ (GCC o Clang)
* `libxml2` i `libxslt` O `lxml`
* `virtualenv`

Per a Ubuntu:
```bash
sudo apt-get install build-essential python3-virtualenv python3
sudo apt-get build-dep python3-lxml
```

Després, a la carpeta de l'aplicació:
```bash
. env.sh
# O
source env.sh
```

[W1]: https://www.python.org/downloads/
[W2]: http://landinghub.visualstudio.com/visual-cpp-build-tools
[W3]: https://www.cairographics.org/download/
