import sys
import os
from win32com.shell import shell
import logging
import argparse
from Tkinter import *
import tkMessageBox

from config import default_config_url
from ui import InstallerUI
from installer_api import InstallerAPI



def get_logfile_path():
        profile = os.getenv('USERPROFILE')
        company_name = "Peachy"
        app_name = 'PeachyInstaller'
        path = os.path.join(profile, 'AppData', 'Local', company_name, app_name)
        if not os.path.exists(path):
            os.makedirs(path)
        return path


def setup_logging(args):
    logging_path = get_logfile_path()
    peachy_logger = logging.getLogger('peachy')
    logfile = os.path.join(logging_path, 'peachyinstaller.log')

    logging_format = '%(levelname)s: %(asctime)s %(module)s - %(message)s'
    logging_level = getattr(logging, args.loglevel.upper(), "INFO")
    if not isinstance(logging_level, int):
        raise ValueError('Invalid log level: %s' % args.loglevel)
    if True:
        peachy_logger = logging.getLogger('peachy')
        peachy_logger.propagate = False
        logFormatter = logging.Formatter(logging_format)

        fileHandler = logging.FileHandler(logfile)
        consoleHandler = logging.StreamHandler()

        fileHandler.setFormatter(logFormatter)
        consoleHandler.setFormatter(logFormatter)

        peachy_logger.addHandler(fileHandler)
        peachy_logger.addHandler(consoleHandler)

        peachy_logger.setLevel(logging_level)
    else:
        logging.basicConfig(filename=logfile, format=logging_format, level=logging_level)
    peachy_logger.info("\n----------------------Logging Started------------------------")


if __name__ == '__main__':
    parser = argparse.ArgumentParser("Configure and print with Peachy Printer")
    parser.add_argument('-l', '--log',     dest='loglevel', action='store',      required=False, default="INFO", help="Enter the loglevel [DEBUG|INFO|WARNING|ERROR] default: WARNING")
    parser.add_argument('-t', '--console', dest='console',  action='store_true', required=False, help="Logs to console not file")
    parser.add_argument('-a', '--alternate-config', dest='alt_config', action='store', required=False, default=default_config_url, help="Alternate url for config file")
    args, unknown = parser.parse_known_args()

    ASADMIN = 'asadmin'
    if sys.argv[-1] != ASADMIN:
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([script] + sys.argv[1:] + [ASADMIN])
        shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable, lpParameters=params)
        sys.exit(0)

    setup_logging(args)
    logger = logging.getLogger('peashy')
    try:
        api = InstallerAPI(args.alt_config)
        result, code, message = api.initialize()
        logger.info('{} -- {} -- {}'.format(result, code, message))
        root = Tk()
        root.wm_title("Peachy Installer")
        root.resizable(width=FALSE, height=FALSE)
        root.geometry('{}x{}'.format(640, 400))
        if not result:
            tkMessageBox.showinfo("Something annoying has occured", message)
            if code == 10304:
                import webbrowser
                webbrowser.open('https://github.com/PeachyPrinter/peachyinstaller/releases', new=0, autoraise=True)
            sys.exit()
        i = InstallerUI(api, master=root)
        i.mainloop()
    except Exception as ex:
        logger.error(ex.message)
        raise
