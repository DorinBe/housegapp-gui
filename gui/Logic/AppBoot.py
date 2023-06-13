from .ConfigParser import ConfigParser
from Logic import Paths, Globals

dest_port = ""
sites_dict = {}

class AppBoot:
    def __init__(self, message_label):
        self.message_label = message_label
        self.dest_port = ""
        self.config = ConfigParser.get_config()
        self.config.read(Paths.ini)
        self.read_settings()
        self.read_plots()

    def read_settings(self):
        """read 'destination ip' and 'destination port' from ini and save in global variables
         to be laster used by PcapLogic.init()"""
        global dest_port
        self.dest_port = str(self.config['SETTINGS']['destination port'])
        dest_port = self.dest_port

    def read_plots(self):
        """reads Globals.section2 section from ini and save in global 'splitted_plots_list' to be later used by
        main.select_plot() """
        global sites_dict
        sites_dict = dict(self.config.items(Globals.section2))


def add_new_param_to_ini(site_name, state):
    global sites_dict
    config = ConfigParser.get_config()
    config.read(Paths.ini)
    cfgfile = open(Paths.ini, 'w')

    val = sites_dict.get('sites')

    if 'selected' in str(state) or 'normal' in str(state):
        if val == "":
            val += site_name
        else:
            val += ':' + site_name
    else:
        val = val.replace(site_name, "")
        val = val.replace('::', ':')

    config.set(Globals.section2, 'sites', val)
    config.write(cfgfile)
    cfgfile.close()

    sites_dict = dict(config.items(Globals.section2))