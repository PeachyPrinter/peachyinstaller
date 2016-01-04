from Tkinter import *

class InstallerAPI(object):
    def check_version(self):
        pass

    def get_items(self):
        return [
            {'id': 1, 'name': "Item 1", 'installed': True},
            {'id': 2, 'name': "Item 2", 'installed': False},
            {'id': 3, 'name': "Item 3", 'installed': False}
            ]

    def get_item(self, id):
        return "This is a name {}".format(id)

    def process(self, id, install=False, remove=False, status_callback=None, complete_callback=None):
        status_callback(id, "Woot")
        complete_callback(id, True)


class Selector(Frame):
    def __init__(self, parent, master, api):
        Frame.__init__(self, master)
        self.parent = parent
        self.install_items = {}
        self._api = api
        self._create_gui()

    def _create_gui(self):
        frame_items = LabelFrame(self, text="Select Items to Add/Remove", height=300)
        row = 0
        for item in self._api.get_items():
            row += 10
            Label(frame_items, text=item['name'], width=30, anchor='w').grid(row=row, column=10)
            if item['installed']:
                self.install_items[item['id']] = IntVar(value=0)
                Checkbutton(frame_items, text='remove', anchor='w', width=6, variable=self.install_items[item['id']], onvalue=-1).grid(row=row, column=20)
            else:
                self.install_items[item['id']] = IntVar(value=0)
                Checkbutton(frame_items, text='add', anchor='w', width=6, variable=self.install_items[item['id']], onvalue=1).grid(row=row, column=20)
        frame_items.grid(row=0, column=0, columnspan=2)
        button_cancel = Button(self, text="Cancel", command=self._cancel)
        button_cancel.grid(row=2, column=0)
        button_proceed = Button(self, text="Continue", command=self._continue)
        button_proceed.grid(row=2, column=1)

    def _cancel(self):
        exit()

    def _continue(self):
        self.parent.install_items = dict([(item, state.get()) for (item, state) in self.install_items.items()])
        self.master.event_generate("<<CloseSelect>>")


class AddRemove(Frame):
    def __init__(self, parent, master, api, items):
        Frame.__init__(self, master)
        self.parent = parent
        self._api = api
        self.items = [(id, status) for (id, status) in items.items() if status != 0]
        self._create_gui()

    def _create_gui(self):
        labelframe = LabelFrame(self, text='Updating applications')
        labelframe.grid(row=1, column=1)
        Label(labelframe, text="App", pady=8, ).grid(row=0, column=0)
        Label(labelframe, text="Action", pady=8, width=10).grid(row=0, column=1)
        Label(labelframe, text="Status", pady=8).grid(row=0, column=2)

        self.app_vars = {}
        y_pos = 0
        for (id, addremove) in self.items:
            y_pos += 1
            name = self._api.get_item(id)
            action = "Add" if addremove == 1 else "Remove"
            colour = "#FFFFFF" if y_pos % 2 == 0 else "#DDDDDD"
            self.app_vars[id] = {
                'name': StringVar(value=name),
                'status': StringVar(value="Getting Ready"),
                'action': StringVar(value=action),
                'complete': False
                }
            Label(labelframe, textvariable=self.app_vars[id]['name'], background=colour, pady=8).grid(row=y_pos, column=0)
            Label(labelframe, textvariable=self.app_vars[id]['action'], background=colour, pady=8, width=10).grid(row=y_pos, column=1)
            Label(labelframe, textvariable=self.app_vars[id]['status'], background=colour, pady=8).grid(row=y_pos, column=2)
        self._process_items()


    def _process_items(self):
        for item_id, status in self.items:
            print(item_id)
            install = True if status == 1 else False
            remove = True if status == -1 else False
            self._api.process(item_id, install=install, remove=remove, status_callback=self.status_callback, complete_callback=self.complete_callback)

    def status_callback(self, id, status):
        print("Status Call")
        self.app_vars[id]['status'].set(status)

    def complete_callback(self, id, success):
        print("Complete call")
        self.app_vars[id]['complete'] = True



class InstallerUI(Frame):
    def __init__(self, api, master):
        Frame.__init__(self, master)
        self.install_items = None
        self._api = api
        self._create_gui()

    def _create_gui(self):
        self.selector = Selector(self, self.master, self._api)
        self.selector.grid(row=1, column=0)
        self.master.bind("<<CloseSelect>>", self._close_select, '+')

    def _create_add_remove_gui(self):
        self.add_remove = AddRemove(self, self.master, self._api, self.install_items)
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
        self._create_add_remove_gui()
        self.master.update()


if __name__ == '__main__':
    api = InstallerAPI()
    root = Tk()
    root.wm_title("Peachy Installer")
    root.resizable(width=FALSE, height=FALSE)
    root.geometry('{}x{}'.format(350, 400))
    i = InstallerUI(api, master=root)
    i.mainloop()
