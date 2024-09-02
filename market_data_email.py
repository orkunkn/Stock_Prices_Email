import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os

print("----- Welcome to Market Data App -----")

# Define the symbols and their corresponding Yahoo Finance tickers
symbols = {
    "eurusd": "EURUSD=X",
    "gbpusd": "GBPUSD=X",
    "usdjpy": "JPY=X",
    "xau": "GC=F",
    "xag": "SI=F",
    "brt": "BZ=F",
    "nas": "^IXIC",
    "dax": "^GDAXI",
    "copper": "HG=F",
    "btc": "BTC-USD",
    "dxy": "DX-Y.NYB",
    "bist100": "XU100.IS"
}

# Set up email parameters
sender_email = ""

# Define the filename
filename = 'user_email.txt'

# Check if the file exists and is not empty
if not os.path.isfile(filename) or os.path.getsize(filename) == 0:
    # File does not exist or is empty, ask the user for their email
    while True:
        receiver_email = input("Enter your email address: ").strip()
        if receiver_email[-1] in {",", ".", "-", ";", "+"} or not all(char in receiver_email for char in ("@", ".")) or all(char in receiver_email for char in ('"')):
            print("Please enter a valid email.")
        else:
            # Save the email to the file
            with open(filename, 'w') as file:
                file.write(receiver_email)
            break

else:
    # File exists and is not empty, read the email from the file
    with open(filename, 'r') as file:
        receiver_email = file.read().strip()

# Get yesterday's date
date = datetime.now() - timedelta(days=1)
formatted_date = date.strftime('%d %B %Y')

# Prepare the email content with HTML
email_content = f"""
<html>
<head>
    <style>
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            border: 1px solid black;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        caption {{
            font-size: 1.5em;
            margin: 0.5em 0;
        }}
    </style>
</head>
<body>
    <table>
        <tr>
            <th>Symbol</th>
            <th>Close</th>
            <th>High</th>
            <th>Low</th>
        </tr>
"""

# Fetch and print the close, day high, and day low prices for each symbol
print("Fetching data...")
for symbol, ticker in symbols.items():
    data = yf.Ticker(ticker)
    # Fetch data for the date entered by the user
    start_date = date.strftime('%Y-%m-%d')
    end_date = (date + timedelta(days=1)).strftime('%Y-%m-%d')
    hist = data.history(start=start_date, end=end_date)
    if not hist.empty:
        if start_date in hist.index.strftime('%Y-%m-%d'):
            prev_day_data = hist.loc[start_date]
            close_price = prev_day_data['Close']
            high_price = prev_day_data['High']
            low_price = prev_day_data['Low']
            email_content += f"""
            <tr>
                <td>{symbol.upper()}</td>
                <td>{close_price:.4f}</td>
                <td>{high_price:.4f}</td>
                <td>{low_price:.4f}</td>
            </tr>
            """
        else:
            email_content += f"""
            <tr>
                <td colspan="5">No data available for {symbol.upper()} on {formatted_date}</td>
            </tr>
            """
    else:
        email_content += f"""
        <tr>
            <td colspan="5">No data available for {symbol.upper()}</td>
        </tr>
        """

email_content += """
    </table>
</body>
</html>
"""

subject = f"{formatted_date} Market Data"

# Create the email
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = subject

# Attach the email content
message.attach(MIMEText(email_content, "html"))

# Send the email
print("Sending email...")
try:
    with smtplib.SMTP("smtp.gmail.com", 587) as server:  # Replace with SMTP server details
        server.starttls()
        server.login(sender_email, "")  # Replace with email password
        server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully.")
except Exception as e:
    print(f"Error sending email: {e}")
