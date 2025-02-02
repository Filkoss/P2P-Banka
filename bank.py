import os
import json
import random
from socket import socket

from bank_account import BankAccount

ACCOUNTS_FILE = "accounts.json"

class Bank:
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.accounts = {}
        self.load_accounts()

    def load_accounts(self):
        if os.path.isfile(ACCOUNTS_FILE):
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for acc_num, balance in data.items():
                    acc = BankAccount(int(acc_num))
                    acc.balance = balance
                    self.accounts[int(acc_num)] = acc

    def save_accounts(self):
        data = {str(acc.account_number): acc.balance for acc in self.accounts.values()}
        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def create_account(self):
        while True:
            acc_number = random.randint(10000, 99999)  # Rozmezí 10000–99999
            if acc_number not in self.accounts:  # Ověření, že číslo účtu již neexistuje
                self.accounts[acc_number] = BankAccount(acc_number)
                self.save_accounts()
                return f"AC {acc_number}/{self.ip_address}"

    def deposit(self, account_number, amount):
        if account_number not in self.accounts:
            return False, "ER Účet neexistuje"
        success, msg = self.accounts[account_number].deposit(amount)
        if success:
            self.save_accounts()
        return success, msg

    def withdraw(self, account_number, amount):
        if account_number not in self.accounts:
            return False, "ER Účet neexistuje"
        success, msg = self.accounts[account_number].withdraw(amount)
        if success:
            self.save_accounts()
        return success, msg

    def get_balance(self, account_number):
        if account_number not in self.accounts:
            return "ER Účet neexistuje"
        balance = self.accounts[account_number].get_balance()
        return f"AB {balance}"

    def remove_account(self, account_number):
        if account_number not in self.accounts:
            return "ER Účet neexistuje"
        balance = self.accounts[account_number].get_balance()
        if balance != 0:
            return "ER Nelze smazat bankovní účet na kterém jsou finance."
        del self.accounts[account_number]
        self.save_accounts()
        return "AR"

    def total_amount(self):
        total = sum(acc.get_balance() for acc in self.accounts.values())
        return f"BA {total}"

    def num_clients(self):
        return f"BN {len(self.accounts)}"

    def get_ip_address(self):
        try:
            # Vytvoříme socket a připojíme se na veřejný server (např. Google DNS)
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Připojení pouze k získání IP
            ip_address = s.getsockname()[0]  # Získání vlastní IP
            s.close()
            return ip_address
        except Exception:
            return "ER Chyba při získávání IP adresy"

    def process_command(data, bank):
        parts = data.split()
        command = parts[0].upper()

        if command == "BC":
            return f"BC {get_ip_address()}"  # Vrátí skutečnou IP adresu

