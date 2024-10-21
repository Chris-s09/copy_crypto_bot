COPY_TRADE_MESSAGE = """
Copy Trade
Wallet: 
`{}`

Copy Trade allows you to copy the buys and sells of any target wallet.
🟢 Indicates a copy trade setup is active.
🟠 Indicates a copy trade setup is paused.

"""

ALERT_MESSAGE = """
Action Alert\!\!\!

Wallet: \`{}\`
Action: {}
Token: \`{}\`
"""

GREETING_MESSAGE = """<b>👋 Welcome {user_first_name}!</b>

Your Wallet:
<code>{wallet_address}</code>

🤖 Copy any wallet

Your Balance:
<code>{user_balance} LAMPORTs</code>

How to find wallet? Step by Step: <a href='www.google.com'>Tutorial</a>
Need help? Support channel <a href='www.google.com'>@botsupport_bot</a>
"""

WSOL = "So11111111111111111111111111111111111111112"

WALLET_SNIPE_MESSAGE = """
<b>👜 Wallet 👇</b><code>{maker}</code>
<b>🔄Transactions:</b> <code>{trading_volume}</code>
<b>🤑Realized PNL:</b> <code>{realized_profit}$</code>
<b>⏰Active Days:</b> <code>245</code>
<b>📅First Activity Time:</b> <code>2/1/2024</code>
<b>📅Last Activity Time:</b> <code>{last_trade_timestamp}</code>
<b>📊Performance 👉<a href='https://dexcheck.ai/app/wallet-analyzer/{maker}'>DexCheckAI</a></b>
    """

MAX_RETRIES = 3

DEPOSIT_MESSAGE = """We currently facilitate transactions with MoonPay for cryptocurrency sales. To sell cryptocurrencies through a third-party platform
You must agree to their terms of service and complete their initial Know Your Customer (KYC) process for the first transaction.

Please click on the button below to Deposit using Credit/Debit Card

Wallet Address <code>{wallet_address}</code>
Currency : <code>SOL</code>
Chain&Protocol : <code>SOL (SPL)</code>"""
