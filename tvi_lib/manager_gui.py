#!/usr/bin/python
import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
from tvi_lib.dbutils import get_ips_from_db, tables_exist, create_tables, get_database_number_len, add_record_to_db, remove_record_from_db, resolve_number_to_ip, get_connection
import ipaddress


class IPManager:
    def __init__(self, root):
        self.root = root
        self.root.title("IP Manager")

        self.db_connection = None
        self.number_length = 0
        self.ip_list = []

        self.listbox = tk.Listbox(root, width=50, height=10)
        self.listbox.pack(pady=10)

        self.add_button = tk.Button(root, text="Lägg till Nummer/IP", command=self.add_ip)
        self.add_button.pack(pady=5)

        self.remove_button = tk.Button(root, text="Ta bort vald", command=self.remove_ip)
        self.remove_button.pack(pady=5)

        self.setup_database()
        self.refresh_list()

    def setup_database(self):
        if not tables_exist("tvi.db"):
            answer = messagebox.askokcancel("Info", "Databasen finns inte, skapa ny?")
            if answer and self.create_database():
                self.db_connection = get_connection('tvi.db')
                self.number_length = get_database_number_len(self.db_connection)
            else:
                exit(0)
        else:
            self.db_connection = sqlite3.connect('tvi.db')
            self.number_length = get_database_number_len(self.db_connection)

    def create_database(self):
        number_length = simpledialog.askinteger("Skapar databas...", prompt="Hur många siffror ska nummer i databasen ha?", initialvalue=4, maxvalue=255, minvalue=0)
        if number_length:
            conn = get_connection('tvi.db')
            create_tables(conn, number_length)
            return True
        return False

    def add_ip(self):
        number = self.get_number_input()
        if not number:
            return

        if self.is_number_exists(number):
            messagebox.showerror("Fel", "Detta nummer finns redan i databasen.")
            return

        ip_address = self.get_ip_input()
        if ip_address:
            add_record_to_db(self.db_connection, number, ip_address)
            self.refresh_list()

    def remove_ip(self):
        selected = self.listbox.curselection()
        if not selected:
            messagebox.showerror("Fel", "Välj en post att ta bort.")
            return

        item_text = self.listbox.get(selected[0])
        number = item_text.split(" - ")[0]
        remove_record_from_db(self.db_connection, number)
        self.refresh_list()

    def refresh_list(self):
        self.ip_list.clear()
        records = get_ips_from_db(self.db_connection)

        for record in records:
            number, ip = record
            ip = ipaddress.ip_address(ip).compressed
            self.ip_list.append([ip, str(number)])

        self.listbox.delete(0, tk.END)
        for combo in self.ip_list:
            self.listbox.insert(tk.END, f"{combo[1]} - {combo[0]}")

    def get_number_input(self):
        number = simpledialog.askstring("Lägg till", f"Ange ett nummer med {self.number_length} siffror:")
        if number and number.isdigit() and len(number) == self.number_length:
            return number
        messagebox.showerror("Fel", f"Numret måste ha {self.number_length} siffror.")
        return None

    def get_ip_input(self):
        ip_address = simpledialog.askstring("Lägg till", "Ange en IP-adress:")
        if ip_address and self.validate_ip(ip_address):
            return ip_address
        messagebox.showerror("Fel", "Ogiltig IP-adress.")
        return None

    def is_number_exists(self, number):
        return resolve_number_to_ip(self.db_connection, number) is not None

    def validate_ip(self, ip):
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False


if __name__ == "__main__":
    root = tk.Tk()
    app = IPManager(root)
    root.mainloop()
