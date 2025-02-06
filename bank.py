import os
import json
import random
import re
import socket
from datetime import datetime  # ✅ Přidáno pro časové razítko

from bank_account import BankAccount

ACCOUNTS_FILE = "accounts.json"
LOG_FILE = "log.txt"
DEFAULT_PORT = 65530  # Výchozí port pro P2P komunikaci


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
        if len(self.accounts) >= (99999 - 10000 + 1):
            return "ER Naše banka nyní neumožňuje založení nového účtu.".ljust(30)

        while True:
            acc_number = random.randint(10000, 99999)
            if acc_number not in self.accounts:
                self.accounts[acc_number] = BankAccount(acc_number)
                self.save_accounts()

                # ✅ **Logování s časem při vytvoření účtu**
                log_transaction(f"[{get_time()}] Vytvořen účet {acc_number} s bankou {self.ip_address}")

                return f"AC {acc_number}/{self.ip_address}".ljust(30)

    def deposit(self, account_number, amount):
        if account_number not in self.accounts:
            return "ER Účet neexistuje".ljust(30)

        if not re.fullmatch(r"[1-9]\d*", str(amount).strip()):
            return "ER Číslo bankovního účtu a částka není ve správném formátu.".ljust(30)

        amount = int(amount)
        success, msg = self.accounts[account_number].deposit(amount)
        if success:
            self.save_accounts()
            log_transaction(f"[{get_time()}] Vklad {amount} na účet {account_number}")
        return msg.ljust(30)

    def withdraw(self, account_number, amount):
        if account_number not in self.accounts:
            return "ER Účet neexistuje".ljust(30)

        if not re.fullmatch(r"[1-9]\d*", str(amount).strip()):
            return "ER Částka musí být kladné číslo.".ljust(30)

        amount = int(amount)
        success, msg = self.accounts[account_number].withdraw(amount)
        if success:
            self.save_accounts()
            log_transaction(f"[{get_time()}] Výběr {amount} z účtu {account_number}")
        return msg.ljust(30)

    def get_balance(self, account_number):
        if account_number not in self.accounts:
            return "ER Účet neexistuje".ljust(30)
        balance = self.accounts[account_number].get_balance()
        return f"AB {balance}".ljust(30)

    def remove_account(self, account_number):
        if account_number not in self.accounts:
            return "ER Účet neexistuje".ljust(30)
        balance = self.accounts[account_number].get_balance()
        if balance != 0:
            return "ER Nelze smazat bankovní účet na kterém jsou finance.".ljust(30)
        del self.accounts[account_number]
        self.save_accounts()
        log_transaction(f"[{get_time()}] Účet {account_number} byl odstraněn")
        return "AR".ljust(30)

    def total_amount(self):
        total = sum(acc.get_balance() for acc in self.accounts.values())
        return f"BA {total}".ljust(30)

    def num_clients(self):
        return f"BN {len(self.accounts)}".ljust(30)

    def get_ip_address(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_address = s.getsockname()[0]
            s.close()
            return ip_address
        except Exception:
            return "ER Chyba při získávání IP adresy".ljust(30)


# 🔴 **Mezibankovní P2P transakce**
def send_request_to_bank(ip, command):
    """Pošle příkaz na jiný bankovní server a vrátí odpověď."""
    try:
        with socket.create_connection((ip, DEFAULT_PORT), timeout=5) as sock:
            sock.sendall((command + "\n").encode('utf-8'))
            response = sock.recv(1024).decode('utf-8').strip()
            return response
    except Exception as e:
        return f"ER Nelze se připojit k bance {ip}: {str(e)}"


# 🔴 **Logování transakcí s časem**
def log_transaction(message):
    """Zapíše zprávu do souboru log.txt s časovou značkou."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{message}\n")


# ✅ **Funkce pro získání aktuálního času**
def get_time():
    """Vrátí aktuální čas ve formátu HH:MM:SS."""
    return datetime.now().strftime("%H:%M:%S")


# 🔧 **Zpracování příkazů**
def process_command(data, bank):
    if not data:
        return "ER Prázdný příkaz".ljust(30)

    parts = data.split()
    command = parts[0].upper()

    if command == "BC":
        return f"BC {bank.ip_address}".ljust(30)

    if command == "AC":
        return bank.create_account().ljust(30)

    if command in ("AD", "AW") and len(parts) == 3:
        account_ip, amount_str = parts[1], parts[2]
        if "/" not in account_ip:
            return "ER Formát čísla účtu není správný".ljust(30)

        acc_number_str, bank_ip = account_ip.split("/", 1)

        if not re.fullmatch(r"[1-9]\d*", amount_str):
            return "ER Číslo bankovního účtu a částka není ve správném formátu.".ljust(30)

        acc_number, amount = int(acc_number_str), int(amount_str)

        if bank_ip != bank.ip_address:
            response = send_request_to_bank(bank_ip, data)
            log_transaction(f"[{get_time()}] Odeslána P2P transakce: {data}")
            return response.ljust(30)

        if command == "AD":
            return bank.deposit(acc_number, amount).ljust(30)
        else:
            return bank.withdraw(acc_number, amount).ljust(30)

    if command == "AB" and len(parts) == 2:
        account_ip = parts[1]
        if "/" not in account_ip:
            return "ER Formát čísla účtu není správný".ljust(30)

        acc_number_str, _ = account_ip.split("/", 1)
        acc_number = int(acc_number_str)
        return bank.get_balance(acc_number).ljust(30)

    if command == "AR" and len(parts) == 2:
        account_ip = parts[1]
        if "/" not in account_ip:
            return "ER Formát čísla účtu není správný".ljust(30)

        acc_number_str, _ = account_ip.split("/", 1)
        acc_number = int(acc_number_str)
        return bank.remove_account(acc_number).ljust(30)

    if command == "BA":
        return bank.total_amount().ljust(30)

    if command == "BN":
        return bank.num_clients().ljust(30)

    return "ER Neznámý příkaz".ljust(30)
