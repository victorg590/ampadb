import os
import os.path
import configparser
import json

class AmpaDbSettings:
    def __init__(self):
        settings_var = os.environ.get('AMPADB_SETTINGS')
        if settings_var:
            settings_files = settings_var.split(os.pathsep)
            for f in settings_files:
                if os.path.isfile(f):
                    self.config = configparser.ConfigParser()
                    self.config.read(f)
            self.settings_file = settings_files[0]
        else:
            self.config = None

    def get(self, key, default=None, raw=False):
        if self.config:
            found = self.config.get('DEFAULT', key, raw=raw, fallback=default)
            if found is not None:
                return found
        found = os.environ.get('AMPADB_' + key.upper())
        if found is not None:
            return found
        if self.config:
            return self.config.get('FALLBACK', key, raw=raw, fallback=default)
        return default

    def getint(self, key, default=None, raw=False):
        if self.config:
            found = self.config.getint('DEFAULT', key, raw=raw, fallback=None)
            if found is not None:
                return found
        try:
            found = int(os.environ.get('AMPADB_' + key.upper()))
        except (ValueError, TypeError):
            found = None
        if found is not None:
            return found
        if self.config:
            return self.config.getint('FALLBACK', key, raw=raw,
                fallback=default)
        return default

    def getfloat(self, key, default=None, raw=False):
        if self.config:
            found = self.config.getfloat('DEFAULT', key, raw=raw, fallback=None)
            if found is not None:
                return found
        try:
            found = float(os.environ.get('AMPADB_' + key.upper()))
        except (ValueError, TypeError):
            found = None
        if found is not None:
            return found
        if self.config:
            return self.config.getfloat('FALLBACK', key, raw=raw,
                fallback=default)
        return default

    def getboolean(self, key, default=None, raw=False):
        if self.config:
            found = self.config.getboolean('DEFAULT', key, raw=raw,
                fallback=None)
            if found is not None:
                return found
        try:
            found = bool(int(os.environ.get('AMPADB_' + key.upper())))
        except (ValueError, TypeError):
            found = None
        if found is not None:
            return found
        if self.config:
            return self.config.getboolean('FALLBACK', key, raw=raw,
                fallback=default)
        return default

    def getjson(self, key, default=None, raw=False):
        if self.config:
            found = self.config.get('DEFAULT', key, raw=raw,fallback=None)
            if found is not None:
                try:
                    return json.loads(found)
                except json.JSONDecodeError:
                    found = None
        found = os.environ.get('AMPADB_' + key.upper())
        if found is not None:
            try:
                return json.loads(found)
            except json.JSONDecodeError:
                found = None
        if self.config:
            try:
                return json.loads(self.config.get('FALLBACK', key, raw=raw,
                    fallback=default))
            except json.JSONDecodeError:
                pass
        return default

    def set(self, key, value):
        os.environ['AMPADB_' + key.upper()] = value

    def setjson(self, key, value):
        return self.set(key, json.dumps(value))
