# Auto Major claimer
Auto claimer for @major

My tg: https://t.me/Zzjjjuuu

## Functionality
| Functional                                                     | Supported |
|----------------------------------------------------------------|:---------:|
| Multithreading                                                 |     ✅     |
| Binding a proxy to a session                                   |     ✅     |
| Auto-player;                                                   |     ✅     |
| Random sleep time between accounts                             |     ✅     |
| Support pyrogram .session                                      |     ✅     |
| Get statistics for all accounts                                |     ✅     |
| Generating unique user-agent for each session                  |     ✅     |
| Completing tasks                                               |     ✅     |
## Settings data/config.py
| Setting                      | Description                                                                                    |
|------------------------------|------------------------------------------------------------------------------------------------|
| **PHONE NUMBER / API_ID / API_HASH** in data/api_config.json         | Platform data from which to launch a Telegram session _(stock - Android)_                      |
| **DELAYS-ACCOUNT**           | Delay between connections to accounts (the more accounts, the longer the delay) _(eg [5, 15])_ |
| **WORKDIR**                  | directory with session _(eg "sessions/")_                                                      |
| **TIMEOUT**                  | timeout in seconds for checking accounts on valid _(eg 30)_                                    |

## Requirements
- Python 3.12 (you can install it [here]([https://www.python.org/downloads/release/python-390/](https://www.python.org/downloads/))) 
- Telegram API_ID and API_HASH (you can get them [here](https://my.telegram.org/auth))

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
## Usage
1. Run the bot:
   ```bash
   python main.py
   ```
