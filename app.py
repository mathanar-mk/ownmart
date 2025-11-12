import tkinter as tk
from tkinter import ttk, messagebox
import tempfile
import os
import qrcode
from PIL import Image, ImageTk

# --------------------
# Configuration
# --------------------
ITEM_PRICES = {
    "Milk (1L)": 62.0,
    "Bread (Loaf)": 45.0,
    "Eggs (6 pcs)": 55.0,
    "Rice (1kg)": 72.0,
    "Sugar (1kg)": 48.0,
    "Apples (1kg)": 140.0,
    "Bananas (1 dozen)": 60.0,
    "Oil (1L)": 165.0,
    "Toothpaste": 95.0,
    "Soap Bar": 35.0,
    "(Products List Customisble)" : 3.00,
}

GST_RATE = 0.05
DISCOUNT_RATE = 0.10
DISCOUNT_THRESHOLD = 1000.0
G_PAY_UPI_ID = "skiranbedi@okhdfcbank"  # 🔁 Change this to your real UPI ID

cart = []

# --------------------
# Utility Functions
# --------------------
def format_money(value):
    return f"₹{value:,.2f}"

def add_to_cart():
    item = item_var.get()
    qty_text = qty_var.get().strip()
    if not item:
        messagebox.showwarning("Select item", "Please choose an item.")
        return

    if not qty_text.isdigit():
        messagebox.showerror("Invalid quantity", "Quantity must be a positive whole number.")
        return

    qty = int(qty_text)
    if qty <= 0:
        messagebox.showerror("Invalid quantity", "Quantity must be greater than zero.")
        return

    unit_price = ITEM_PRICES[item]
    line_total = unit_price * qty
    cart.append((item, qty, unit_price, line_total))
    refresh_receipt()
    qty_var.set("1")

def refresh_receipt():
    receipt_box.config(state="normal")
    receipt_box.delete("1.0", tk.END)

    receipt_box.insert(tk.END, "         Own Mart RECEIPT\n")
    receipt_box.insert(tk.END, "-----------------------------------\n")
    receipt_box.insert(tk.END, "Item                    Qty    Amount\n")
    receipt_box.insert(tk.END, "-----------------------------------\n")

    subtotal = 0.0
    for (name, qty, price, line_total) in cart:
        subtotal += line_total
        name_col = f"{name[:20]:20}"
        qty_col = f"{qty:>3}"
        amt_col = f"{format_money(line_total):>10}"
        receipt_box.insert(tk.END, f"{name_col}   {qty_col}   {amt_col}\n")

    receipt_box.insert(tk.END, "-----------------------------------\n")
    gst = subtotal * GST_RATE
    discount = DISCOUNT_RATE * subtotal if subtotal >= DISCOUNT_THRESHOLD else 0.0
    total = subtotal + gst - discount

    receipt_box.insert(tk.END, f"Subtotal:          {format_money(subtotal)}\n")
    receipt_box.insert(tk.END, f"GST (5%):          {format_money(gst)}\n")
    receipt_box.insert(tk.END, f"Discount:          {format_money(discount)}\n")
    receipt_box.insert(tk.END, "-----------------------------------\n")
    receipt_box.insert(tk.END, f"Grand Total:       {format_money(total)}\n")
    receipt_box.insert(tk.END, "-----------------------------------\n")
    receipt_box.config(state="disabled")

    subtotal_var.set(format_money(subtotal))
    gst_var.set(format_money(gst))
    discount_var.set(format_money(discount))
    total_var.set(format_money(total))

def clear_cart():
    cart.clear()
    refresh_receipt()

def calculate_now():
    refresh_receipt()

def delete_last():
    if cart:
        cart.pop()
        refresh_receipt()
    else:
        messagebox.showinfo("Cart empty", "There is nothing to remove.")

def print_receipt():
    content = receipt_box.get("1.0", tk.END).strip()
    if not content:
        messagebox.showinfo("No data", "There is no receipt to print.")
        return

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as temp_file:
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        if os.name == "nt":
            os.startfile(temp_path, "print")
        else:
            os.system(f"lpr {temp_path}")
        messagebox.showinfo("Print", "Receipt sent to printer successfully.")
    except Exception as e:
        messagebox.showerror("Print Error", f"Error printing receipt:\n{e}")

# --------------------
# GOOGLE PAY QR GENERATION
# --------------------
def pay_with_gpay():
    total_text = total_var.get().replace("₹", "").replace(",", "")
    try:
        total_amount = float(total_text)
        if total_amount <= 0:
            messagebox.showwarning("No Amount", "Add items before generating QR for payment.")
            return
    except ValueError:
        messagebox.showwarning("Error", "Invalid total amount.")
        return

    upi_link = (
        f"upi://pay?pa={G_PAY_UPI_ID}&pn=OwnMart&am={total_amount:.2f}&cu=INR&tn=OwnMart+Payment"
    )

    qr = qrcode.make(upi_link)
    temp_path = os.path.join(tempfile.gettempdir(), "gpay_qr.png")
    qr.save(temp_path)

    qr_window = tk.Toplevel(root)
    qr_window.title("Pay with Google Pay")
    qr_window.geometry("300x380")
    qr_window.resizable(False, False)

    ttk.Label(qr_window, text="Scan to Pay with Google Pay", font=("Segoe UI", 10, "bold")).pack(pady=10)

    img = Image.open(temp_path)
    img = img.resize((250, 250))
    qr_img = ImageTk.PhotoImage(img)

    qr_label = ttk.Label(qr_window, image=qr_img)
    qr_label.image = qr_img
    qr_label.pack(pady=10)

    ttk.Label(qr_window, text=f"Amount: ₹{total_amount:.2f}", font=("Segoe UI", 11, "bold")).pack(pady=5)
    ttk.Label(qr_window, text=f"UPI ID: {G_PAY_UPI_ID}", font=("Segoe UI", 9)).pack(pady=5)

    ttk.Button(qr_window, text="Close", command=qr_window.destroy).pack(pady=10)

# --------------------
# UI SETUP
# --------------------
root = tk.Tk()
root.title("Mini POS - Retail Billing")
root.geometry("760x540")
root.resizable(False, False)

top = ttk.LabelFrame(root, text="Add Item")
top.place(x=15, y=10, width=730, height=110)

ttk.Label(top, text="Item").grid(row=0, column=0, padx=10, pady=10, sticky="w")
item_var = tk.StringVar()
item_combo = ttk.Combobox(top, textvariable=item_var, values=list(ITEM_PRICES.keys()), state="readonly", width=28)
item_combo.grid(row=0, column=1, padx=5, pady=10, sticky="w")
item_combo.current(0)

ttk.Label(top, text="Unit Price").grid(row=0, column=2, padx=10, pady=10, sticky="w")
price_var = tk.StringVar(value="—")
price_label = ttk.Label(top, textvariable=price_var)
price_label.grid(row=0, column=3, padx=5, pady=10, sticky="w")

def on_item_change(event=None):
    chosen = item_var.get()
    if chosen:
        price_var.set(format_money(ITEM_PRICES[chosen]))

item_combo.bind("<<ComboboxSelected>>", on_item_change)
on_item_change()

ttk.Label(top, text="Quantity").grid(row=1, column=0, padx=10, pady=5, sticky="w")
qty_var = tk.StringVar(value="1")
qty_entry = ttk.Entry(top, textvariable=qty_var, width=10)
qty_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

add_btn = ttk.Button(top, text="Add to Cart", command=add_to_cart)
add_btn.grid(row=1, column=2, padx=10, pady=5, sticky="w")

del_btn = ttk.Button(top, text="Remove Last", command=delete_last)
del_btn.grid(row=1, column=3, padx=5, pady=5, sticky="w")

receipt_frame = ttk.LabelFrame(root, text="Receipt")
receipt_frame.place(x=15, y=130, width=470, height=370)
receipt_box = tk.Text(receipt_frame, height=18, width=56, state="disabled")
receipt_box.pack(padx=8, pady=8, fill="both", expand=True)

totals = ttk.LabelFrame(root, text="Totals")
totals.place(x=500, y=130, width=245, height=220)

subtotal_var = tk.StringVar(value="₹0.00")
gst_var = tk.StringVar(value="₹0.00")
discount_var = tk.StringVar(value="₹0.00")
total_var = tk.StringVar(value="₹0.00")

row = 0
for label_text, var in [
    ("Subtotal:", subtotal_var),
    ("GST (5%):", gst_var),
    ("Discount:", discount_var),
    ("Grand Total:", total_var),
]:
    ttk.Label(totals, text=label_text).grid(row=row, column=0, padx=10, pady=10, sticky="w")
    ttk.Label(totals, textvariable=var, font=("Segoe UI", 10, "bold")).grid(row=row, column=1, padx=5, pady=10, sticky="e")
    row += 1

actions = ttk.Frame(root)
actions.place(x=500, y=360, width=245, height=160)

calc_btn = ttk.Button(actions, text="Calculate Totals", command=calculate_now)
calc_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

clear_btn = ttk.Button(actions, text="Clear Cart", command=clear_cart)
clear_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

print_btn = ttk.Button(actions, text="Print Receipt", command=print_receipt)
print_btn.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

pay_btn = ttk.Button(actions, text="Pay with GPay", command=pay_with_gpay)
pay_btn.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

exit_btn = ttk.Button(actions, text="Exit", command=root.destroy)
exit_btn.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

refresh_receipt()
root.mainloop()
