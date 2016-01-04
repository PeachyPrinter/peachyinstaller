from Tkinter import *

class InstallerAPI(object):
    def check_version(self):
        pass

    def get_items(self):
        return [
            {'id': 1, 'name': "Item 1", 'installed': True},
            {'id': 1, 'name': "Item 2", 'installed': False},
            {'id': 1, 'name': "Item 3", 'installed': False}
            ]


class Selector(Frame):
    def __init__(self, master, api):
        Frame.__init__(self, master)
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
                self.install_items[item['id']] = Checkbutton(frame_items, text='remove', anchor='w', width=6)
                self.install_items[item['id']].grid(row=row, column=20)
            else:
                self.install_items[item['id']] = Checkbutton(frame_items, text='add', anchor='w', width=6)
                self.install_items[item['id']].grid(row=row, column=20)
        frame_items.grid(row=0, column=0, columnspan=2)
        button_cancel = Button(self, text="Cancel", command=self._cancel)
        button_cancel.grid(row=2, column=0)
        button_proceed = Button(self, text="Continue", command=self._continue)
        button_proceed.grid(row=2, column=1)

    def _cancel(self):
        exit()

    def _continue(self):
        self.master.install_items = self.install_items
        self.master.event_generate("<<CloseSelect>>")


class InstallerUI(Frame):
    def __init__(self, api, master):
        Frame.__init__(self, master)
        self._install_items = {}
        self._api = api
        self._create_gui()

    def _create_gui(self):
        Label(text="HEAD").grid(row=0, column=0)
        self.selector = Selector(self.master, self._api)
        self.selector.grid(row=1, column=0)
        self.master.bind("<<CloseSelect>>", self._close_select, '+')

    def _close_select(self, event):
        self.selector.grid_forget()
        hi = Label(text='HASDF')
        hi.grid(row=0, column=0)
        self.master.update()


if __name__ == '__main__':
    api = InstallerAPI()
    root = Tk()
    root.wm_title("Peachy Installer")
    root.resizable(width=FALSE, height=FALSE)
    root.geometry('{}x{}'.format(350, 400))
    i = InstallerUI(api, master=root)
    i.mainloop()
