import os
import os.path
import configparser
import json


class AmpaDbSettings:
    def __init__(self):
        settings_var = os.environ.get('AMPADB_SETTINGS')
        if settings_var:
            settings_files = settings_var.split(os.pathsep)
            self.settings_file = None
            self.config = configparser.ConfigParser(interpolation=None)
            self.config.add_section('FALLBACK')
            self.config.read(settings_files)
            self.settings_file = self.get('save_cfg', default=None)
        else:
            self.config = None
            self.settings_file = None

    def get(self, key, default=None):
        if self.config:
            found = self.config.get('DEFAULT', key, fallback=default)
            if found is not None:
                return found
        found = os.environ.get('AMPADB_' + key.upper())
        if found is not None:
            return found
        if self.config:
            return self.config.get('FALLBACK', key, fallback=default)
        return default

    def getint(self, key, default=None):
        if self.config:
            found = self.config.getint('DEFAULT', key, fallback=None)
            if found is not None:
                return found
        try:
            found = int(os.environ.get('AMPADB_' + key.upper()))
        except (ValueError, TypeError):
            found = None
        if found is not None:
            return found
        if self.config:
            return self.config.getint('FALLBACK', key, fallback=default)
        return default

    def getfloat(self, key, default=None):
        if self.config:
            found = self.config.getfloat('DEFAULT', key, fallback=None)
            if found is not None:
                return found
        try:
            found = float(os.environ.get('AMPADB_' + key.upper()))
        except (ValueError, TypeError):
            found = None
        if found is not None:
            return found
        if self.config:
            return self.config.getfloat('FALLBACK', key, fallback=default)
        return default

    def getboolean(self, key, default=None):
        if self.config:
            found = self.config.getboolean('DEFAULT', key, fallback=None)
            if found is not None:
                return found
        try:
            found = bool(int(os.environ.get('AMPADB_' + key.upper())))
        except (ValueError, TypeError):
            found = None
        if found is not None:
            return found
        if self.config:
            return self.config.getboolean('FALLBACK', key, fallback=default)
        return default

    def getjson(self, key, default=None):
        found = self.get(key, default=None)
        if not found:
            return default
        try:
            return json.loads(found)
        except json.JSONDecodeError:
            return default

    def set(self, key, value):
        os.environ['AMPADB_' + key.upper()] = value
        if self.config:
            self.config.set('FALLBACK', key, value)
            if self.settings_file:
                with open(self.settings_file) as sf:
                    self.config.write(sf)

    def setjson(self, key, value):
        return self.set(key, json.dumps(value))
