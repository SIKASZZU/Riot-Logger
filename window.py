import tkinter as tk
from tkinter import font

# Account selection function
account_selected = None  # username, pass
user_input_value = ""

def on_button_click(root, key):
    global account_selected
    account_selected = key
    root.destroy()

def on_submit(root, entry):
    global user_input_value
    user_input_value = entry.get()
    root.destroy()

def activate_window(accounts_list):
    global user_input_value

    ################# ACCS #################
    acc_details = {}
    for account in accounts_list:
        username = account[0]
        acc_name = account[1]
        acc_pass = account[2]
        acc_details[username] = (acc_name, acc_pass)

    ################# TK #################

    # Calculate the window height based on the number of accounts
    max_height = 600
    button_height = 40  # Height of each button (including padding)
    num_accounts = len(accounts_list)  # Number of accounts
    window_height = num_accounts * button_height + 150  # Additional space for input field
    window_height = min(window_height, max_height)

    # Create the main Tkinter window
    root = tk.Tk()
    root.title("Account Selection")
    root.geometry(f"400x{window_height}")
    root.config(bg="#F0F0F0")

    # Custom font
    custom_font = font.Font(family="Helvetica", size=12, weight="bold")

    # Header label
    label = tk.Label(root, text="Choose your account", font=custom_font, bg="#F0F0F0", fg="#333333")
    label.pack(pady=(20, 10))

    # Create a frame to hold the buttons
    frame = tk.Frame(root, bg="#F0F0F0")
    frame.pack(pady=20)

    # Button styling
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

    # Create a button for each account
    for key in acc_details.keys():
        button = tk.Button(frame, text=key, command=lambda key=key: on_button_click(root, key), **button_style)
        button.pack(pady=5)

    # User input field
    input_label = tk.Label(root, text="Or enter manually:", font=custom_font, bg="#F0F0F0", fg="#333333")
    input_label.pack(pady=(10, 5))
    
    user_input = tk.Entry(root, font=custom_font, width=25)
    user_input.pack(pady=5)
    
    submit_button = tk.Button(root, text="Submit", command=lambda: on_submit(root, user_input), **button_style)
    submit_button.pack(pady=10)

    # Run the Tkinter event loop
    root.mainloop()
    
    return user_input_value