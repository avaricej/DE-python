from datetime import datetime
import re
import csv
import json 

class BankAccount:

    account_type = "base"
    next_account_number = 1000

    def __init__(self, owner: str, balance: float = 0):

        owner_match = re.fullmatch(r"[А-ЯЁA-Z][а-яёa-z]+ [А-ЯЁA-Z][а-яёa-z]+", owner)
        if not owner_match:
            raise ValueError("Некорректное имя")
        self.owner = owner
        self.history = []
        if balance < 0:
            raise ValueError("Баланс меньше 0")
        self.account_number = f"ACC-{self.next_account_number}"
        BankAccount.next_account_number += 1
        self.balance = balance

    def deposit(self, amount: float = 0):
        if amount <= 0:

            # self.history.append(
            #     f"deposit {amount} {datetime.now()} Ошибка при операции error"
            # )
            self.history.append(
                {
                    "type": "deposit",
                    "amount": amount,
                    "datetime": datetime.now(),
                    "new_balance": self.balance,
                    "status": "fail",
                }
            )
            raise ValueError("Ошибка при операции")

        self.balance += amount

        self.history.append(
            {
                "type": "deposit",
                "amount": amount,
                "datetime": datetime.now(),
                "new_balance": self.balance,
                "status": "success",
            }
        )
        # self.history.append(
        #                 f"deposit {amount} {datetime.now()} Ошибка при операции error"
        #             )

    def withdraw(self, amount: float = 0):
        if amount <= 0:
            self.history.append(
                {
                    "type": "withdraw",
                    "datetime": datetime.now(),
                    "amount": amount,
                    "new_balance": self.balance,
                    "status": "fail",
                }
            )
            raise ValueError("Сумма списания должна быть положительной")
        if self.balance < amount:
            self.history.append(
                {
                    "type": "withdraw",
                    "datetime": datetime.now(),
                    "amount": amount,
                    "new_balance": self.balance,
                    "status": "fail",
                }
            )

        else:
            self.balance -= amount
            self.history.append(
                {
                    "type": "withdraw",
                    "datetime": datetime.now(),
                    "amount": amount,
                    "new_balance": self.balance,
                    "status": "success",
                }
            )
    def _parse_row(self, row):
        if self.account_type == "savings":
            allowed = {"deposit", "withdraw", "interest"}
        else:
            allowed = {"deposit", "withdraw"}
            
        if row['status'] not in ['fail', 'success']:
            return None
        
        try:
            amount = float(row['amount'])
            datetime.fromisoformat(row['date'])
        except (ValueError, KeyError, TypeError):
            return None
       
        if amount <= 0:
            return None   
        
        if row["operation"] not in allowed:
            return None
        return row
        
    def get_balance(self):
        return self.balance
    
    def _apply_row(self,row):
        
        # record = dict()
        record= {
            "type" : row["operation"],

            "amount" : float(row["amount"]),

            "datetime" : datetime.fromisoformat(row["date"]),

            "new_balance" : float(row["balance_after"]),
            "status" : row["status"]
        }
        self.history.append(record)
        self.balance = float(row["balance_after"])
        

    def show_history(self):
        return self.history

    def top_operations(self, min_amount, limit):

        result = [
            rec
            for rec in self.history
            if rec["status"] == "success" and rec["amount"] >= min_amount
        ][-limit:]
        
        return result

    def load_from_json(self,path):
        
        with open(path,'r', encoding='utf-8') as file:
            a = json.load(file)
            valid_rows = [row for row in a if row['account_number'] ==self.account_number and self._parse_row(row) is not None]
            for row in valid_rows:
                self._apply_row(row)
                
            # print(valid_rows)
            return valid_rows
        
    def load_from_csv(self, path):
        
        with open(path , 'r', newline='') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            valid_rows = [row for row in rows if row['account_number'] == self.account_number and self._parse_row(row) is not None]
            
            for row in valid_rows:
                self._apply_row(row)
            
        return valid_rows
            
            

man1 = BankAccount(owner="Carl Morris", balance=456)
man2 = BankAccount(owner="Chris Lou", balance=9996)


class CheckingAccount(BankAccount):
    account_type = "checking"
    pass


man1.deposit(300)
man1.withdraw(200)
# print(man1.balance, man1.account_number)
user = CheckingAccount("Ivan Perov", 0)
# print(user.get_balance())


class SavingsAccount(BankAccount):
    account_type = "savings"

    def plus_procent(self, rate: int):
        if rate <= 0:
            self.history.append(
                {
                    "type": "interest",
                    "datetime": datetime.now(),
                    "new_balance": self.balance,
                    "amount": 0,
                    "status": "fail",
                }
            )
            raise ValueError("Процент не положительный")
        amount = self.balance * rate / 100
        self.balance = self.balance + amount

        self.history.append(
            {
                "type": "interest",
                "datetime": datetime.now(),
                "new_balance": self.balance,
                "amount": amount,
                "status": "success",
            }
        )

    def withdraw(self, amount: float):

        if (0.5 * self.balance) < amount:
            self.history.append(
                {
                    "type": "withdraw",
                    "amount": amount,
                    "datetime": datetime.now(),
                    "new_balance": self.balance,
                    "status": "fail",
                }
            )

        else:
            super().withdraw(amount)


anna = SavingsAccount("Anna Smith", 1000)


anna.plus_procent(5)

anna.withdraw(400)

anna.withdraw(600)

# print(anna.top_operations(100, 5),anna.top_operations(30, 1))

check_acc = CheckingAccount("Ivan Petrov", 0)
check_acc.account_number = "ACC-100001"

# check_acc.load_from_csv('transactions_dirty.csv')
check_acc.load_from_json('transactions_dirty.json')
print("Баланс после загрузки:", check_acc.get_balance())
print(check_acc.show_history()[:2])