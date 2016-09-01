import os
import os.path
import configparser

class AmpaDbSettings:
    def __init__(self):
        settings_file = os.environ.get('AMPADB_SETTINGS')
        if settings_file and os.path.isfile(settings_file):
            self.config = configparser.ConfigParser()
            self.config.read(settings_file)
            self.settings_file = settings_file
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

    def set(self, key, value):
        if self.config:
            self.config['DEFAULT'][key] = value
            with open(self.settings_file, 'w') as cfg:
                config.write(cfg)
        os.environ['AMPADB_' + key.upper()] = value
