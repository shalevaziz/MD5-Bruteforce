import tkinter as tk
from tkinter import font as tkfont
import time
import server
from hashlib import md5
from threading import Thread

class SampleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self,*args, **kwargs)
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", underline=True)

        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.main = Menu_Frame(parent=self.container, controller=self)

        self.main.grid(row=0, column=0, sticky="nsew")

        self.main.tkraise()
        self.mainloop()

    def build_server(self, md5, client_length, total_length):
        print(md5, client_length, total_length)
        self.server = server.Server(md5, client_length, total_length)
        self.server_thread = Thread(target=self.server.mainloop)
        self.server_thread.start()
        self.page = Management_Frame(parent=self.container, controller=self)
        self.page.grid(row=0, column=0, sticky="nsew")
        self.page.tkraise()
        Thread(target=self.page.mainloop).start()
        self.geometry("740x500")

class Menu_Frame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__()
        self.build_menu_frame(parent, controller)

    def build_menu_frame(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.controller.title("Config Menu")
        label = tk.Label(self, text="Config", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        self.entry_dimensions = 100
        self.pedy = 30
        self.ipedy = 20

        self.start_butt = tk.Button(self, text="Start", command=self.start)

        self.md5 = EntryWithPlaceholder(self, "MD5 HASH", "black")
        self.total_len = EntryWithPlaceholder(self, "TOTAL LENGTH", "black")
        self.cli_len = EntryWithPlaceholder(self, "CLIENT LENGTH", "black")

        self.md5.pack(pady=10)
        self.total_len.pack(pady=10)
        self.cli_len.pack(pady=10)
        
        self.status_label = tk.Label(self, font=("Helvetica", 16), fg="red")
        self.status_label.pack(pady=10)

        self.start_butt.pack(pady=10)

    def start(self):
        if self.md5.get() == "MD5 HASH" or self.cli_len.get() == "CLIENT LENGTH" or self.total_len.get() == "TOTAL LENGTH" or not self.md5.get().isalnum() or not self.cli_len.get().isnumeric() or not self.total_len.get().isnumeric():
            self.status_label.config(text="Invalid input")
            return

        if len(self.md5.get()) != 32:
            if not self.md5.get().isalpha():
                self.status_label.config(text="Invalid input")
                return
            if not self.md5.get().islower():
                self.status_label.config(text="Invalid input")
                return
            self.controller.build_server(str(md5(self.md5.get().encode()).hexdigest()), int(self.cli_len.get()), int(self.total_len.get()))
        else:
            self.controller.build_server(self.md5.get(), int(self.cli_len.get()), int(self.total_len.get()))

class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey'):
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        text_font = tkfont.Font(family='Helvetica', size=14, weight="bold")
        self.configure(justify="center", width=30, font=text_font)
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self,args):
        if not self.get():
            self.put_placeholder()

class Management_Frame(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.label1 = tk.Label(self, text="Server Status: running, IP:{ip}, Port:{port}".format(
            ip=controller.server.ip, port=controller.server.port
            ), font=("Helvetica", "18"))
        self.label1.grid(row=0, column=0, columnspan=4, sticky=tk.N)
        self.label2 = tk.Label(self,text="Connected Clients: {num}".format(num=len(self.controller.server.addresses)), font=("Helvetica", "18"))
        self.label2.grid(row=1, column=0, columnspan=4, sticky=tk.N)
        
        self.listbox_ip = tk.Listbox(self)
        self.listbox_ip.grid(row=3, column=0,sticky=tk.N)
        self.listbox_ip_label = tk.Label(self, text="IP")
        self.listbox_ip_label.grid(row=2, column=0, sticky=tk.N)
        self.listbox_ip_label.config(font=("Helvetica", "14"))
        self.listbox_ip.config(font=("Helvetica", "12"), height=100, width=20)
        
        self.listbox_port = tk.Listbox(self)
        self.listbox_port.grid(row=3, column=1, sticky=tk.N)
        self.listbox_port_label = tk.Label(self, text="Port")
        self.listbox_port_label.grid(row=2, column=1, sticky=tk.N)
        self.listbox_port_label.config(font=("Helvetica", "14"))
        self.listbox_port.config(font=("Helvetica", "12"), height=100, width=20)

        self.listbox_work = tk.Listbox(self)
        self.listbox_work.grid(row=3, column=2, sticky=tk.N)
        self.listbox_work_label = tk.Label(self, text="Work")
        self.listbox_work_label.grid(row=2, column=2, sticky=tk.N)
        self.listbox_work_label.config(font=("Helvetica", "14"))
        self.listbox_work.config(font=("Helvetica", "12"), height=100, width=20)

        self.listbox_time = tk.Listbox(self)
        self.listbox_time.grid(row=3, column=3, sticky=tk.N)
        self.listbox_time_label = tk.Label(self, text="Time")
        self.listbox_time_label.grid(row=2, column=3, sticky=tk.N)
        self.listbox_time_label.config(font=("Helvetica", "14"))
        self.listbox_time.config(font=("Helvetica", "12"), height=100, width=20)
        
        self.addresses = {}

    def udpate_disconnects(self, disconnects):
        for addr in disconnects:
            index = self.addresses[addr]
            self.listbox_ip.delete(index)
            self.listbox_port.delete(index)
            self.listbox_work.delete(index)
            self.listbox_time.delete(index)
                
            for key, value in self.addresses.items():
                if value > index:
                    self.addresses[key] -= 1

            del self.addresses[addr]
    
    def update_connections(self):
        self.label2.config(text="Connected Clients: {num}".format(num=len(self.controller.server.addresses)))
        for addr in self.controller.server.addresses:
            if addr not in self.addresses:
                self.addresses[addr] = self.listbox_ip.size()
                self.listbox_ip.insert(self.listbox_ip.size(), addr[0])
                self.listbox_port.insert(self.listbox_port.size(), addr[1])
                self.listbox_work.insert(self.listbox_work.size(), self.controller.server.cur_work[addr])
                self.listbox_time.insert(self.listbox_time.size(), round((time.time() - self.controller.server.last_seen[addr]), 1))
            else:
                index = self.addresses[addr]
                
                cur_work = self.controller.server.cur_work[addr]
                if cur_work != self.listbox_work.get(index):
                    self.listbox_work.delete(index)
                    self.listbox_work.insert(index, cur_work)
                
                cur_time = round((time.time() - self.controller.server.last_seen[addr]), 1)
                if cur_time != self.listbox_time.get(index):
                    self.listbox_time.delete(index)
                    self.listbox_time.insert(index, round((time.time() - self.controller.server.last_seen[addr]), 1))
        
    def mainloop(self):
        while not self.controller.server.found:
            disconnects = self.controller.server.get_disconnects()
            if disconnects:
                self.udpate_disconnects(disconnects)
                print(self.addresses, self.controller.server.addresses)
            if self.controller.server.addresses:
                self.update_connections()
        self.label1.config(text="Server Status: found, password:{password}".format(password=self.controller.server.passwd))
        self.label2.config(text="".format(num=len(self.controller.server.addresses)))
        self.udpate_disconnects(self.controller.server.addresses)
        
        
if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()