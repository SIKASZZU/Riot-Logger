import tkinter as tk
from tkinter import font, messagebox

# Create a button for each account
def on_button_click(root, account_details):
    global account_selected
    account_selected = account_details
    root.destroy()


def activate_window(accounts_list):
    # Build acc_details from accounts_list for display and management
    acc_details = {account[0]: (account[1], account[2]) for account in accounts_list}

    # Create the main Tkinter window
    root = tk.Tk()
    root.title("Add Accounts")
    # Set initial window size; it’s resizable by default
    max_height = 600
    button_height = 40  # Approximate height per button including padding
    num_accounts = len(accounts_list)
    window_height = min(num_accounts * button_height + 150, max_height)
    root.geometry(f"400x{window_height}")
    root.config(bg="#F0F0F0")

    # Custom font for consistency
    custom_font = font.Font(family="Helvetica", size=12, weight="bold")

    # Header label
    label = tk.Label(root, text="Account List", font=custom_font, bg="#F0F0F0", fg="#333333")
    label.pack(pady=(20, 10))

    # Frame to hold account buttons
    frame = tk.Frame(root, bg="#F0F0F0")
    frame.pack(pady=20)

    # Button styling (without command since no selection is needed)
    button_style = {
        'font': custom_font,
        'bg': "#4CAF50",
        'fg': "white",
        'width': 20,
        'height': 2,
        'bd': 0,
        'relief': "flat",
        'activebackground': "#45a049",
        'activeforeground': "white"
    }

    # Create buttons for existing accounts. Click account, TK window closes, acc details go to main.py
    for key in acc_details.keys():
        account_details = acc_details[key]
        button = tk.Button(frame, text=key, command=lambda key=key: on_button_click(root, account_details), **button_style)
        button.pack(pady=5)

    # Input field for adding new accounts
    input_label = tk.Label(root, text="Enter: username, acc_name, password", font=custom_font, bg="#F0F0F0", fg="#333333")
    input_label.pack(pady=(10, 5))
    
    user_input = tk.Entry(root, font=custom_font, width=25)
    user_input.pack(pady=5)
    
    def on_submit():
        input_str = user_input.get()
        try:
            parts = input_str.split(',')
            if len(parts) != 3:
                raise ValueError
            username, acc_name, password = [p.strip() for p in parts]
            if username in acc_details:
                messagebox.showerror("Error", "Username already exists.")
                return
            # Add to accounts_list and acc_details
            accounts_list.append((username, acc_name, password))
            acc_details[username] = (acc_name, password)
            # Append to file
            with open("acc_details.txt", "a") as f:
                f.write(f"{username}, {acc_name}, {password}\n")
            # Add new button to frame
            new_button = tk.Button(frame, text=username, **button_style)
            new_button.pack(pady=5)
            # Clear entry field
            user_input.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Invalid input format. Please enter: username, acc_name, password")

    # Submit button
    submit_button = tk.Button(root, text="Add Account", command=on_submit, **button_style)
    submit_button.pack(pady=10)

    # Start the main event loop
    root.mainloop()

    return account_selected

# Example usage
if __name__ == "__main__":
    # Load existing accounts from file (or start with empty list if file doesn’t exist)
    try:
        with open("acc_details.txt", "r") as f:
            accounts_list = [tuple(line.strip().split(", ")) for line in f if line.strip()]
    except FileNotFoundError:
        accounts_list = []
    activate_window(accounts_list)