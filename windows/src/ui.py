import sys
import os
import logging
from functools import partial
from Tkinter import *

logger = logging.getLogger('peachy')


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
            self.install_items[item.id] = {}
            self.install_items[item.id]['remove'] = IntVar(value=0)
            self.install_items[item.id]['upgrade'] = IntVar(value=0)
            self.install_items[item.id]['install'] = IntVar(value=0)

            if item.current_version:
                Checkbutton(frame_items, text='Remove', anchor='w', width=6, variable=self.install_items[item.id]['remove'], onvalue=1, offvalue=0, command=self._can_continue).grid(row=row, column=20)
                if item.current_version != item.available_version:
                    Checkbutton(frame_items, text='Upgrade', anchor='w', width=6, variable=self.install_items[item.id]['upgrade'], onvalue=1, offvalue=0, command=self._can_continue).grid(row=row, column=30)
            else:
                Checkbutton(frame_items, text='Install', anchor='w', width=6, variable=self.install_items[item.id]['install'], onvalue=1, offvalue=0, command=self._can_continue).grid(row=row, column=20)
        frame_items.grid(row=0, column=0, columnspan=2)

        Label(self, anchor=W,  pady=8).grid(row=3, column=0, sticky=W)

        Label(self, anchor=W, text="Install to", pady=8, width=11).grid(row=4, column=0, sticky=W)
        Entry(self, textvariable=self.install_path, width=85).grid(row=4, column=1, sticky=W)

        Label(self, anchor=W, pady=8).grid(row=5, column=0, sticky=W)

        button_cancel = Button(self, text="Cancel", command=self._cancel)
        button_cancel.grid(row=6, column=0, sticky=W)
        self.button_proceed = Button(self, text="Continue", command=self._continue, state=DISABLED)
        self.button_proceed.grid(row=6, column=1, sticky=E)

    def _cancel(self):
        sys.exit()

    def _get_action(self, state):
        codes = dict([(action, value.get()) for (action, value) in state.items()])
        if codes['install'] == 1:
            return 'install'
        if codes['upgrade'] == 1:
            return 'upgrade'
        if codes['remove'] == 1:
            return 'remove'
        else:
            return None

    def _can_continue(self):
        all_items = [(self._get_action(check)) for (item, check) in self.install_items.items()]
        check = ''.join([item for item in all_items if item is not None])
        if len(check) > 0:
            self.button_proceed.configure(state=NORMAL)
        else:
            self.button_proceed.configure(state=DISABLED)

    def _continue(self):
        try:
            all_items = [(item, self._get_action(check)) for (item, check) in self.install_items.items()]
            self.parent.install_items = dict([(item, action) for (item, action) in all_items if action is not None])
            self.parent.install_path = self.install_path.get()
            self.master.event_generate("<<CloseSelect>>")
        except Exception as ex:
            logger.error(ex.message)


class AddRemove(Frame):
    def __init__(self, parent, master, api, items, install_path):
        Frame.__init__(self, master, padx=5, pady=5)
        self.parent = parent
        self.install_path = install_path
        self._api = api
        self.items = items
        self._create_gui()

    def _create_gui(self):
        logger.info('Creating Progress Gui')
        labelframe = LabelFrame(self, text='Updating applications')
        labelframe.grid(row=1, column=1)
        Label(labelframe, anchor=W, text="App", pady=8, width=30).grid(row=0, column=0, sticky=W)
        Label(labelframe, anchor=W, text="Action", pady=8, width=10).grid(row=0, column=1, sticky=W)
        Label(labelframe, anchor=W, text="Status", pady=8, width=46).grid(row=0, column=2, sticky=W)

        logger.info('Adding Applications')
        self.app_vars = {}
        y_pos = 0
        for (id, action) in self.items:
            y_pos += 1
            application = self._api.get_item(id)
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
        logger.info('Process Selected Items')
        for item_id, action in self.items:
            if action:
                status_partial = partial(self.status_callback, id=item_id)
                complete_partial = partial(self.complete_callback, id=item_id)
                self._api.process(item_id, self.install_path, action, status_callback=status_partial, complete_callback=complete_partial)
        logger.info('All items Processing')
        self.master.after(1000, self.check_complete)

    def check_complete(self):
        complete = [value['complete'] for (key, value) in self.app_vars.items()]
        if False in complete:
            logger.info("Checking if complete")
            self.master.after(1000, self.check_complete)
        else:
            logger.info("Complete")
            self._update_ui()

    def _update_ui(self):
        button_exit = Button(self, text="Exit", command=sys.exit)
        button_exit.grid(row=99, column=1, sticky=E)

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
            if state in ['install', 'upgrade', 'remove']:
                logger.info("{} item {}".format(state, item))
            else:
                logger.info("Do nothing for item: {}".format(item))
        items = [(id, state) for (id, state) in self.install_items.items() if state in ['install', 'upgrade', 'remove']]
        if items:
            logger.info("Processing {} items".format(len(items)))
            self._create_add_remove_gui(items)
        else:
            logger.info("Woe there bucko, No application selected for install or remove.\nExiting installation")
            sys.exit()
        self.master.update()
