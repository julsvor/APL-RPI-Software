#!/usr/bin/python
import os, sys

os.environ['PYTHONPATH'] = '/usr/local/lib/tvi/lib/python3.11/site-packages/'
sys.path = sys.path + [os.environ['PYTHONPATH']]

import tkinter as tk
from tkinter import messagebox, simpledialog
import mariadb # type: ignore

from tvi_lib.tvi_dbutils import get_ips_from_db, database_exists, create_db, get_database_number_len, add_pair_to_db, remove_pair_from_db, resolve_number_to_ip
import ipaddress


class IPManager:
    def __init__(self, root):
        self.root = root
        self.root.title("IP Manager")

        self.ip_list = []  # Dictionary to store number-IP pairs

        self.listbox = tk.Listbox(root, width=50, height=10)
        self.listbox.pack(pady=10)

        self.add_button = tk.Button(root, text="Lägg till Nummer/IP", command=self.add_ip)
        self.add_button.pack(pady=5)

        self.remove_button = tk.Button(root, text="Ta bort vald", command=self.remove_ip)
        self.remove_button.pack(pady=5)

        if database_exists(user="tvi_dbcli_dbuser", password="readwrite") == False:
            answer = messagebox.askokcancel("Databasen finns inte, skapa ny?")
            if answer == True:
                number_length = simpledialog.askinteger("Skapar databas", prompt="Hur många siffror ska nummer i databasen ha?", initialvalue=4, maxvalue=255, minvalue=0)
                create_db("tvi_dbcli_dbuser", "readwrite", number_length)

        
        
        self.db_connection = mariadb.connect(host="localhost", user="tvi_dbcli_dbuser", password="readwrite", database="tvi")
        self.number_length = get_database_number_len(self.db_connection)

        self.refresh_list()

    def add_ip(self):
        number = simpledialog.askstring("Lägg till", f"Ange ett nummer med {self.number_length} siffror:")
        if number == None:
            return
        if not (number and number.isdigit() and len(number) == self.number_length):
            messagebox.showerror("Fel", f"Numret måste ha {self.number_length} siffror.")
            return
        if resolve_number_to_ip(self.db_connection, number) != None:
            messagebox.showerror("Fel", "Detta nummer finns redan i databasen.")
            return

        ip_address = simpledialog.askstring("Lägg till", "Ange en IP-adress:")
        if ip_address == None:
            return
        if not (ip_address and self.validate_ip(ip_address)):
            messagebox.showerror("Fel", "Ogiltig IP-adress.")
            return

        add_pair_to_db(self.db_connection, number, ip_address)
        self.refresh_list()

    def remove_ip(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showerror("Fel", "Välj en post att ta bort.")
            return

        item_text = self.listbox.get(selected[0])
        number = item_text.split(" - ")[0]

        remove_pair_from_db(self.db_connection, number)

        self.refresh_list()

    def refresh_list(self):
        
        self.ip_list.clear()

        records = get_ips_from_db(self.db_connection)

        for record in records:
            number, ip = record
            number: str = str(number)
            ip: str = ipaddress.ip_address(ip).compressed

            self.ip_list.append([ip, number])

        self.listbox.delete(0, tk.END)
        for combo in self.ip_list:
            ip = combo[0]
            number = combo[1]
            self.listbox.insert(tk.END, f"{number} - {ip}")

    def validate_ip(self, ip):
        try:
            return True if ipaddress.ip_address(ip).compressed else False
        except Exception as e:
            return False


if __name__ == "__main__":
    root = tk.Tk()
    app = IPManager(root)
    root.mainloop()