import configparser as cp
from . import Paths

class ConfigParser:
    __config = cp.ConfigParser()

    @staticmethod
    def get_config():
        return ConfigParser.__config 

    @staticmethod
    def change_settings(to_change:str, new_value:str):
        """change settings in ini file"""
        ConfigParser.__config.read(Paths.ini)
        cfgfile = open(Paths.ini, 'w')
        ConfigParser.__config.set('SETTINGS', to_change, new_value)
        ConfigParser.__config.write(cfgfile)
        cfgfile.close()