import sys
import os

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inventory_data.txt")
BILLING_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "billing_history.txt")

class Product:
    def __init__(self, product_id, name, price, stock):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = stock

    def __str__(self):
        return f"{self.product_id:<6}{self.name:<15}{self.price:<10.2f}{self.stock:<8}"

    def to_line(self):
        return f"{self.product_id},{self.name},{self.price},{self.stock}\n"

    @staticmethod
    def from_line(line):
        parts = line.strip().split(",")
        product_id = int(parts[0])
        name = parts[1]
        price = float(parts[2])
        stock = int(parts[3])
        return Product(product_id, name, price, stock)

class InventoryManagementSystem:
    def __init__(self):
        self.inventory = []
        self.product_count = 0
        self.load_inventory()

    def load_inventory(self):
        if not os.path.exists(DATA_FILE):
            return

        try:
            with open(DATA_FILE, "r") as file:
                lines = file.readlines()

            for line in lines:
                line = line.strip()
                if line:
                    product = Product.from_line(line)
                    self.inventory.append(product)

            self.product_count = len(self.inventory)
            print(f"Loaded {self.product_count} product(s) from previous session ({DATA_FILE}).")

        except (OSError, ValueError, IndexError) as e:
            print(f"Warning: Could not read existing data file ({e}). Starting with an empty inventory.")
            self.inventory = []
            self.product_count = 0

    def save_inventory(self):
        try:
            with open(DATA_FILE, "w") as file:
                for product in self.inventory:
                    file.write(product.to_line())
        except OSError as e:
            print(f"Warning: Could not save data to file ({e}). Your changes may be lost on exit.")

    def _find_by_id(self, product_id):
        for product in self.inventory:
            if product.product_id == product_id:
                return product
        return None

    def _find_by_name(self, name):
        for product in self.inventory:
            if product.name.lower() == name.lower():
                return product
        return None

    def add_product(self):
        print("\n----- ADD NEW PRODUCT -----")
        try:
            product_id = int(input("Enter Product ID: ").strip())
        except ValueError:
            print("Invalid Product ID. Must be a number.")
            return

        if self._find_by_id(product_id) is not None:
            print(f"Error: Product ID {product_id} already exists. Use Update Stock instead.")
            return

        name = input("Enter Product Name: ").strip()
        if not name:
            print("Error: Product Name cannot be empty.")
            return
        if "," in name:
            print("Error: Product Name cannot contain a comma (used as the file separator).")
            return

        try:
            price = float(input("Enter Product Price: ").strip())
            stock = int(input("Enter Product Stock Quantity: ").strip())
        except ValueError:
            print("Invalid Price/Stock. Must be numeric.")
            return

        if price < 0 or stock < 0:
            print("Error: Price and Stock cannot be negative.")
            return

        new_product = Product(product_id, name, price, stock)
        self.inventory.append(new_product)
        self.product_count += 1
        self.save_inventory()

        print(f"Product '{name}' added successfully. (Total products: {self.product_count})")

    def display_inventory(self):
        print("\n----- CURRENT INVENTORY -----")
        if not self.inventory:
            print("Inventory is empty. Please add products first.")
            return

        print(f"{'ID':<6}{'Name':<15}{'Price':<10}{'Stock':<8}")
        print("-" * 40)
        for product in self.inventory:
            print(product)
        print("-" * 40)
        print(f"Total Products: {self.product_count}")

    def search_product(self):
        print("\n----- SEARCH PRODUCT -----")
        print("Search by: 1. Product ID   2. Product Name")
        choice = input("Enter choice (1/2): ").strip()

        product = None
        if choice == "1":
            try:
                pid = int(input("Enter Product ID: ").strip())
                product = self._find_by_id(pid)
            except ValueError:
                print("Invalid Product ID.")
                return
        elif choice == "2":
            name = input("Enter Product Name: ").strip()
            product = self._find_by_name(name)
        else:
            print("Invalid choice.")
            return

        if product:
            print("\nProduct Found:")
            print(f"{'ID':<6}{'Name':<15}{'Price':<10}{'Stock':<8}")
            print(product)
        else:
            print("Product Not Found.")

    def process_billing(self):
        print("\n----- BILLING -----")
        if not self.inventory:
            print("Inventory is empty. Cannot process billing.")
            return

        try:
            product_id = int(input("Enter Product ID: ").strip())
            quantity = int(input("Enter Quantity Required: ").strip())
        except ValueError:
            print("Invalid input. Product ID and Quantity must be numbers.")
            return

        if quantity <= 0:
            print("Error: Quantity must be greater than zero.")
            return

        product = self._find_by_id(product_id)
        if product is None:
            print("Product Not Found.")
            return

        if product.stock < quantity:
            print(f"Error: Insufficient stock. Available stock: {product.stock}")
            return

        total_amount = product.price * quantity

        print("\n========= BILL RECEIPT =========")
        print(f"Product   : {product.name}")
        print(f"Price     : Rs.{product.price:.2f}")
        print(f"Quantity  : {quantity}")
        print(f"Total     : Rs.{total_amount:.2f}")
        print("=================================")

        self.update_stock_after_sale(product, quantity)
        self._log_bill(product, quantity, total_amount)

    def _log_bill(self, product, quantity, total_amount):
        try:
            with open(BILLING_FILE, "a") as file:
                file.write(
                    f"Product: {product.name} | Qty: {quantity} | "
                    f"Price: {product.price:.2f} | Total: {total_amount:.2f}\n"
                )
        except OSError:
            pass

    def update_stock_after_sale(self, product, sold_quantity):
        product.stock -= sold_quantity
        self.save_inventory()
        print(f"Stock Updated: {product.name} stock is now {product.stock}.")

    def update_stock_manual(self):
        print("\n----- UPDATE STOCK (RESTOCK) -----")
        if not self.inventory:
            print("Inventory is empty. Please add products first.")
            return

        try:
            product_id = int(input("Enter Product ID: ").strip())
        except ValueError:
            print("Invalid Product ID.")
            return

        product = self._find_by_id(product_id)
        if product is None:
            print("Product Not Found.")
            return

        print(f"Current stock for '{product.name}': {product.stock}")
        try:
            added_quantity = int(input("Enter quantity to ADD to stock: ").strip())
        except ValueError:
            print("Invalid quantity.")
            return

        if added_quantity < 0:
            print("Error: Quantity to add cannot be negative.")
            return

        product.stock += added_quantity
        self.save_inventory()
        print(f"Stock Updated: {product.name} stock is now {product.stock}.")

    def view_billing_history(self):
        print("\n----- BILLING HISTORY -----")
        if not os.path.exists(BILLING_FILE):
            print("No bills have been generated yet.")
            return

        try:
            with open(BILLING_FILE, "r") as file:
                lines = file.readlines()
        except OSError as e:
            print(f"Warning: Could not read billing history ({e}).")
            return

        lines = [line for line in lines if line.strip()]
        if not lines:
            print("No bills have been generated yet.")
            return

        print("-" * 60)
        for i, line in enumerate(lines, start=1):
            print(f"{i}. {line.strip()}")
        print("-" * 60)
        print(f"Total Bills Recorded: {len(lines)}")

    def exit_system(self):
        self.save_inventory()
        print(f"\nAll records saved to '{DATA_FILE}'.")
        print("Thank You for Using Inventory Management System")
        sys.exit(0)

    def main_menu(self):
        print("=====================================================")
        print("       INVENTORY MANAGEMENT & BILLING SYSTEM")
        print("=====================================================")

        while True:
            print("\n----------- MAIN MENU -----------")
            print("1. Add Product")
            print("2. Display Inventory")
            print("3. Search Product")
            print("4. Process Billing")
            print("5. Update Stock")
            print("6. View Billing History")
            print("7. Exit Application")
            print("----------------------------------")

            choice = input("Enter your choice (1-7): ").strip()

            if choice == "1":
                self.add_product()
            elif choice == "2":
                self.display_inventory()
            elif choice == "3":
                self.search_product()
            elif choice == "4":
                self.process_billing()
            elif choice == "5":
                self.update_stock_manual()
            elif choice == "6":
                self.view_billing_history()
            elif choice == "7":
                self.exit_system()
            else:
                print("Invalid choice. Please select an option between 1 and 7.")

if __name__ == "__main__":
    system = InventoryManagementSystem()
    try:
        system.main_menu()
    except KeyboardInterrupt:
        system.save_inventory()
        print(f"\n\nInterrupted. Records saved to '{DATA_FILE}'. Goodbye!")
        sys.exit(0)