def process_command(data, bank):
    if not data:
        return "ER Prázdný příkaz"

    parts = data.split()
    command = parts[0].upper()

    if command == "BC":
        return f"BC {bank.ip_address}"

    elif command == "AC":
        return bank.create_account()

    elif command == "AD" and len(parts) == 3:
        account_ip = parts[1]
        amount_str = parts[2]
        if "/" in account_ip:
            acc_number_str, _ = account_ip.split("/", 1)
        else:
            return "ER Formát čísla účtu není správný"
        try:
            acc_number = int(acc_number_str)
            amount = int(amount_str)
        except ValueError:
            return "ER číslo bankovního účtu a částka není ve správném formátu."
        success, msg = bank.deposit(acc_number, amount)
        return msg

    elif command == "AW" and len(parts) == 3:
        account_ip = parts[1]
        amount_str = parts[2]
        if "/" in account_ip:
            acc_number_str, _ = account_ip.split("/", 1)
        else:
            return "ER Formát čísla účtu není správný"
        try:
            acc_number = int(acc_number_str)
            amount = int(amount_str)
        except ValueError:
            return "ER číslo bankovního účtu a částka není ve správném formátu."
        success, msg = bank.withdraw(acc_number, amount)
        return msg

    elif command == "AB" and len(parts) == 2:
        account_ip = parts[1]
        if "/" in account_ip:
            acc_number_str, _ = account_ip.split("/", 1)
        else:
            return "ER Formát čísla účtu není správný"
        try:
            acc_number = int(acc_number_str)
        except ValueError:
            return "ER Formát čísla účtu není správný"
        return bank.get_balance(acc_number)

    elif command == "AR" and len(parts) == 2:
        account_ip = parts[1]
        if "/" in account_ip:
            acc_number_str, _ = account_ip.split("/", 1)
        else:
            return "ER Formát čísla účtu není správný"
        try:
            acc_number = int(acc_number_str)
        except ValueError:
            return "ER Formát čísla účtu není správný"
        return bank.remove_account(acc_number)

    elif command == "BA":
        return bank.total_amount()

    elif command == "BN":
        return bank.num_clients()

    else:
        return "ER Neznámý příkaz"
