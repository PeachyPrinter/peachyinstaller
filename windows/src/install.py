from Tkinter import *
import tkMessageBox
from installer_api import InstallerAPIStub



class Selector(Frame):
    def __init__(self, parent, master, api):
        Frame.__init__(self, master, padx=50, pady=5)
        self.parent = parent
        self.install_items = {}
        self._api = api
        self._create_gui()

    def _create_gui(self):
        frame_items = LabelFrame(self, text="Select Items to Add/Remove", height=300)
        row = 0
        for item in self._api.get_items():
            row += 10
            Label(frame_items, text=item['name'], width=30, anchor='w', pady=8).grid(row=row, column=10)
            if item['installed']:
                self.install_items[item['id']] = IntVar(value=0)
                Checkbutton(frame_items, text='remove', anchor='w', width=6, variable=self.install_items[item['id']], onvalue=-1).grid(row=row, column=20)
                self.install_items[item['id']] = IntVar(value=0)
                Checkbutton(frame_items, text='upgrade', anchor='w', width=6, variable=self.install_items[item['id']], onvalue=2).grid(row=row, column=30)
            else:
                self.install_items[item['id']] = IntVar(value=0)
                Checkbutton(frame_items, text='add', anchor='w', width=6, variable=self.install_items[item['id']], onvalue=1).grid(row=row, column=20)
        frame_items.grid(row=0, column=0, columnspan=2)
        button_cancel = Button(self, text="Cancel", command=self._cancel)
        button_cancel.grid(row=2, column=0, sticky=W)
        button_proceed = Button(self, text="Continue", command=self._continue)
        button_proceed.grid(row=2, column=1, sticky=E)

    def _cancel(self):
        exit()

    def _continue(self):
        self.parent.install_items = dict([(item, state.get()) for (item, state) in self.install_items.items()])
        self.master.event_generate("<<CloseSelect>>")


class AddRemove(Frame):
    def __init__(self, parent, master, api, items):
        Frame.__init__(self, master, padx=5, pady=5)
        self.parent = parent
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
            name = self._api.get_item(id)
            action = "Add" if addremove == 1 else "Remove"
            colour = "#FFFFFF" if y_pos % 2 == 0 else "#DDDDDD"
            self.app_vars[id] = {
                'name': StringVar(value=name),
                'status': StringVar(value="Getting Ready"),
                'action': StringVar(value=action),
                'complete': False
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

    def _create_add_remove_gui(self, items):
        self.add_remove = AddRemove(self, self.master, self._api, items)
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
            exit()
        self.master.update()


if __name__ == '__main__':
    api = InstallerAPIStub()
    root = Tk()
    root.wm_title("Peachy Installer")
    root.resizable(width=FALSE, height=FALSE)
    root.geometry('{}x{}'.format(640, 400))
    i = InstallerUI(api, master=root)
    i.mainloop()
