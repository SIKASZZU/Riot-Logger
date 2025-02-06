import tkinter as tk
from tkinter import font
from acc_details import acc_details  # Ensure acc_details is a dictionary with account info

# Account selection function
account_selected = None
def on_button_click(root, key):
    global account_selected
    account_selected = key
    root.destroy()

def activate_window():
    # Calculate the window height based on the number of accounts
    max_height = 600
    button_height = 40  # Height of each button (including padding)
    num_accounts = len(acc_details)  # Number of accounts
    window_height = num_accounts * button_height + 400  # 100 for padding and header
    print(num_accounts, window_height)
    # Ensure the window height doesn't exceed max_height
    window_height = min(window_height, max_height)

    # Create the main Tkinter window
    root = tk.Tk()
    root.title("Account Selection")
    root.geometry(f"400x{window_height}")  # Set window size dynamically
    root.config(bg="#F0F0F0")  # Set background color

    # Custom font
    custom_font = font.Font(family="Helvetica", size=12, weight="bold")

    # Header label
    label = tk.Label(root, text="Choose your account", font=custom_font, bg="#F0F0F0", fg="#333333")
    label.pack(pady=(20, 10))

    # Create a frame to hold the buttons and keep them centered
    frame = tk.Frame(root, bg="#F0F0F0")
    frame.pack(pady=20)

    # Button styling
    button_style = {
        'font': custom_font,
        'bg': "#4CAF50",  # Green background
        'fg': "white",
        'width': 20,
        'height': 2,
        'bd': 0,
        'relief': "flat",
        'activebackground': "#45a049",
        'activeforeground': "white"
    }

    # Create a button for each account in the acc_details dictionary
    for key in acc_details.keys():
        button = tk.Button(frame, text=key, command=lambda key=key: on_button_click(root, key), **button_style)
        button.pack(pady=5)

    # Run the Tkinter event loop
    root.mainloop()

    # Print the selected account after window closes
    print('Account Selected:', account_selected)
    return account_selected