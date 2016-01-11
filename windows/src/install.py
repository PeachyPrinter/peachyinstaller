import sys
import os
from win32com.shell import shell
import logging
import argparse
from functools import partial
from Tkinter import *
import tkMessageBox

from installer_api import InstallerAPI


class Selector(Frame):
    def __init__(self, parent, master, api):
        Frame.__init__(self, master, padx=10, pady=5)
        self.parent = parent
        self.install_items = {}
        self.install_path = StringVar(value="C:\\Program Files\\")
        self._api = api
        self._create_gui()

    def _create_gui(self):
        frame_items = LabelFrame(self, text="Select Items to Add/Remove", height=300)
        row = 0
        for item in self._api.get_items():
            row += 10
            Label(frame_items, text=item.name, width=30, anchor='w', pady=8).grid(row=row, column=10)
            if item.current_version:
                self.install_items[item.id] = IntVar(value=0)
                Checkbutton(frame_items, text='Remove', anchor='w', width=6, variable=self.install_items[item.id], onvalue=-1).grid(row=row, column=20)
                self.install_items[item.id] = IntVar(value=0)
                Checkbutton(frame_items, text='Upgrade', anchor='w', width=6, variable=self.install_items[item.id], onvalue=2).grid(row=row, column=30)
            else:
                self.install_items[item.id] = IntVar(value=0)
                Checkbutton(frame_items, text='Add', anchor='w', width=6, variable=self.install_items[item.id], onvalue=1).grid(row=row, column=20)
        frame_items.grid(row=0, column=0, columnspan=2)

        Label(self, anchor=W,  pady=8).grid(row=3, column=0, sticky=W)

        Label(self, anchor=W, text="Install to", pady=8, width=11).grid(row=4, column=0, sticky=W)
        Entry(self, textvariable=self.install_path, width=85).grid(row=4, column=1, sticky=W)

        Label(self, anchor=W, pady=8).grid(row=5, column=0, sticky=W)

        button_cancel = Button(self, text="Cancel", command=self._cancel)
        button_cancel.grid(row=6, column=0, sticky=W)
        button_proceed = Button(self, text="Continue", command=self._continue)
        button_proceed.grid(row=6, column=1, sticky=E)

    def _cancel(self):
        sys.exit()

    def _continue(self):
        self.parent.install_items = dict([(item, state.get()) for (item, state) in self.install_items.items()])
        self.parent.install_path = self.install_path.get()
        self.master.event_generate("<<CloseSelect>>")


class AddRemove(Frame):
    def __init__(self, parent, master, api, items, install_path):
        Frame.__init__(self, master, padx=5, pady=5)
        self.parent = parent
        self.install_path = install_path
        self._api = api
        self.items = items
        self._create_gui()

    def _create_gui(self):
        labelframe = LabelFrame(self, text='Updating applications')
        labelframe.grid(row=1, column=1)
        Label(labelframe, anchor=W, text="App", pady=8, width=30).grid(row=0, column=0, sticky=W)
        Label(labelframe, anchor=W, text="Action", pady=8, width=10).grid(row=0, column=1, sticky=W)
        Label(labelframe, anchor=W, text="Status", pady=8, width=46).grid(row=0, column=2, sticky=W)

        self.app_vars = {}
        y_pos = 0
        for (id, addremove) in self.items:
            y_pos += 1
            application = self._api.get_item(id)
            action = "Add" if addremove == 1 else "Remove"
            colour = "#FFFFFF" if y_pos % 2 == 0 else "#DDDDDD"
            self.app_vars[id] = {
                'name': StringVar(value=application.name),
                'status': StringVar(value="Getting Ready"),
                'action': StringVar(value=action),
                'complete': False,
                'error': None
                }
            Label(labelframe, anchor=W, textvariable=self.app_vars[id]['name'], background=colour, pady=8, width=30).grid(row=y_pos, column=0, sticky=W)
            Label(labelframe, anchor=W, textvariable=self.app_vars[id]['action'], background=colour, pady=8, width=10).grid(row=y_pos, column=1, sticky=W)
            Label(labelframe, anchor=W, textvariable=self.app_vars[id]['status'], background=colour, pady=8, width=46).grid(row=y_pos, column=2, sticky=W)
        self._process_items()

    def _process_items(self):
        for item_id, status in self.items:
            print(item_id)
            install = True if status == 1 else False
            remove = True if status == -1 else False
            status_partial = partial(self.status_callback, id=item_id)
            complete_partial = partial(self.complete_callback, id=item_id)
            self._api.process(item_id, self.install_path, install=install, remove=remove, status_callback=status_partial, complete_callback=complete_partial)

    def status_callback(self, status, id=None):
        self.app_vars[id]['status'].set(status)

    def complete_callback(self, success, message, id=None):
        if not success:
            self.app_vars[id]['status'].set(message)
            self.app_vars[id]['error'] = message
        self.app_vars[id]['complete'] = True


class InstallerUI(Frame):
    def __init__(self, api, master):
        Frame.__init__(self, master)
        self.install_items = None
        self.install_path = None
        self._api = api
        self._create_gui()

    def _create_gui(self):
        self.selector = Selector(self, self.master, self._api)
        self.selector.grid(row=1, column=0)
        self.master.bind("<<CloseSelect>>", self._close_select, '+')

    def _create_add_remove_gui(self, items):
        self.add_remove = AddRemove(self, self.master, self._api, items, self.install_path)
        self.add_remove.grid()

    def _close_select(self, event):
        self.selector.grid_forget()
        for item, state in self.install_items.items():
            if state == 0:
                print "Do nothing for item: {}".format(item)
            if state == -1:
                print "Remove item: {}".format(item)
            if state == 1:
                print "Install item: {}".format(item)
        items = [(id, status) for (id, status) in self.install_items.items() if status != 0]
        if items:
            self._create_add_remove_gui(items)
        else:
            tkMessageBox.showinfo("Woe there bucko", "No application selected for install or remove.\nExiting installation")
            sys.exit()
        self.master.update()


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
    peachy_logger.info("Logging Started")


if __name__ == '__main__':
    default_config_url = "https://raw.githubusercontent.com/PeachyPrinter/peachyinstaller/master/config.json"
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
    logger = logging.getLogger('peachy')
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
            sys.exit()
        i = InstallerUI(api, master=root)
        i.mainloop()
    except Exception as ex:
        logger.error(ex.message)
        raise
