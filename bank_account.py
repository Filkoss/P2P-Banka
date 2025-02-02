class BankAccount:
    def __init__(self, account_number):
        self.account_number = account_number
        self.balance = 0

    def deposit(self, amount):
        if amount < 0:
            return False, "ER Neplatná částka"
        self.balance += amount
        return True, "AD"

    def withdraw(self, amount):
        if amount > self.balance:
            return False, "ER Není dostatek finančních prostředků"
        self.balance -= amount
        return True, "AW"

    def get_balance(self):
        return self.balance
