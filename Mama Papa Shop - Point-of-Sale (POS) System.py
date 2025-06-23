#!/usr/bin/env python
# coding: utf-8

# In[3]:


import csv
import random

class Authenticator:
    _credentials = {"AliNaqvi": "mypassword"}
    _attempt_limit = 3

    def login(self):
        for attempt in range(self._attempt_limit):
            uid = input("Please enter userid: ")
            pwd = input("Please enter password: ")
            if self._credentials.get(uid) == pwd:
                print("Welcome to the POS System")
                return True
            else:
                print("Invalid User ID or Password")
        print("Your account has been locked out. Please contact your system admin.")
        return False


class Item:
    def __init__(self, upc, desc, max_qty, threshold, reorder_qty, available_qty, price):
        self.upc = upc.strip()
        self.description = desc.strip()
        self.max_qty = int(max_qty.strip())
        self.threshold = int(threshold.strip())
        self.reorder_qty = int(reorder_qty.strip())
        self.stock = int(available_qty.strip())
        self.price = float(price.strip())


class Inventory:
    def __init__(self):
        self.catalog = {}

    def load(self, filepath):
        try:
            with open(filepath, newline='') as file:
                reader = csv.reader(file)
                next(reader)  # skip header
                for row in reader:
                    if len(row) >= 7:
                        try:
                            item = Item(*row[:7])
                            self.catalog[item.upc] = item
                        except ValueError:
                            continue
        except FileNotFoundError:
            print("File not found.")
        except PermissionError:
            print("Permission denied")

    def get_item(self, upc):
        return self.catalog.get(upc)

    def list_low_stock(self):
        low_stock = [
            item for item in self.catalog.values()
            if item.stock <= item.threshold
        ]
        return low_stock


class Transaction:
    def __init__(self):
        self.items = {}
        self.receipt = str(random.randint(10000000, 99999999))
        self.total = 0.0

    def add(self, item, qty):
        if qty <= 0:
            print("Quantity must be positive")
            return
        self.items[item] = self.items.get(item, 0) + qty

    def display_items(self):
        print("\nYou entered:")
        for item, qty in self.items.items():
            print(f"{qty} {item.description}")

    def calculate_total(self):
        self.total = sum(item.price * qty for item, qty in self.items.items())
        print(f"Your total is: {self.total:.2f}")

    def process_return(self, all_receipts):
        receipt_id = input("Please Enter the receipt number: ")
        if receipt_id not in all_receipts:
            print("Receipt not found.")
            return

        previous_sale = all_receipts[receipt_id]
        print("1 = Return Single item, 2 = Return All Items")
        opt = input("Please select your option: ").strip()

        if opt == '1':
            upc = input("Please enter UPC to be returned ")
            item_to_return = None
            for product in previous_sale.items:
                if product.upc == upc:
                    item_to_return = product
                    break
            if not item_to_return:
                print("Item not found in receipt.")
                return
            try:
                qty = int(input("Please Enter quantity "))
                if qty <= 0:
                    print("Quantity must be positive.")
                    return
                if qty > previous_sale.items[item_to_return]:
                    print("Quantity exceeds purchased amount.")
                    return
                previous_sale.items[item_to_return] -= qty
                if previous_sale.items[item_to_return] == 0:
                    del previous_sale.items[item_to_return]
                refund = qty * item_to_return.price
                print(f"\nYou entered: {qty} {item_to_return.description}")
                print(f"Return Amount : {refund:.2f}")
            except ValueError:
                print("Invalid quantity.")
        elif opt == '2':
            confirm = input("Are you sure you want to return all items? Y=yes, N=No ").strip().upper()
            if confirm == 'Y':
                total_refund = 0.0
                for item, qty in previous_sale.items.items():
                    print(f"You entered: {qty} {item.description} Returned")
                    total_refund += item.price * qty
                previous_sale.items.clear()
                print(f"Return Amount : {total_refund:.2f}")
            else:
                print("Return cancelled.")
        else:
            print("Invalid option.")


def main():
    print("Welcome to the POS System")
    auth = Authenticator()
    if not auth.login():
        return

    inventory = Inventory()
    inventory.load("C:/Users/racha/Downloads/RetailStoreItemData (1).txt")
    all_receipts = {}

    while True:
        print("Please select your options")
        print("1 = New Sale, 2 = Return Item/s, 3 = Backroom Operations, 9 = Exit Application")
        choice = input("Please select your option: ").strip()

        if choice == '1':
            print("New Sale")
            txn = Transaction()
            while True:
                upc = input("Please Enter the UPC ")
                item = inventory.get_item(upc)
                if not item:
                    print("You entered: Item not found.")
                    continue
                print(f"You entered: {item.description}")
                try:
                    qty = int(input("Please Enter quantity "))
                    txn.add(item, qty)
                    print(f"The price is: {item.price:.2f}")
                except ValueError:
                    print("Invalid quantity.")
                    continue
                print("1 = Sell another item, 2 = Return Item/s, 9 = Complete Sale")
                follow_up = input("Please select your option: ").strip()
                if follow_up == '9':
                    break
                elif follow_up == '2':
                    txn.process_return(all_receipts)

            print(f"Your receipt number is {txn.receipt}")
            txn.calculate_total()
            txn.display_items()
            all_receipts[txn.receipt] = txn

        elif choice == '2':
            print("Return Item/s")
            dummy_txn = Transaction()
            dummy_txn.process_return(all_receipts)

        elif choice == '3':
            print("\nBackroom Operations:")
            print("1 = View Low Inventory Items")
            print("9 = Return to Main Menu")
            sub_opt = input("Please enter your option: ").strip()
            if sub_opt == '1':
                print("\nItems that need restocking:")
                low_stock_items = inventory.list_low_stock()
                if not low_stock_items:
                    print("All items are sufficiently stocked")
                else:
                    for item in low_stock_items:
                        print(f"UPC: {item.upc}, Description: {item.description}, On Hand: {item.stock}, Threshold: {item.threshold}")
            elif sub_opt == '9':
                continue
            else:
                print("Invalid option")

        elif choice == '9':
            print("Thank You")
            break
        else:
            print("select valid option")

if __name__ == "__main__":
    main()


# In[ ]:




