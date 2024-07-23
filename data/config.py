DELAYS = {
    'ACCOUNT': [5, 30],  # delay between connections to accounts (the more accounts, the longer the delay)
    'MAJOR_SLEEP': [5, 60*20],
    'PLAY': [5, 15],   # delay between play in seconds
    'ERROR_PLAY': [60, 180],    # delay between errors in the game in seconds
    'CLAIM': [600, 1800],   # delay in seconds before claim points every 8 hours
    'REPEAT': [300, 600],
    'BUY_CARD': [2, 5]   # delay before buy a upgrade cards
}

# proxy type for tg client
PROXY_TYPES = {
    "TG": "http",  # proxy type for tg client. "socks4", "socks5" and "http" are supported
    "REQUESTS": "http"  # proxy type for requests. "http" for https and http proxys, "socks5" for socks5 proxy.
}

BLACKLIST_TASK = []

# session folder (do not change)
WORKDIR = "sessions/"

# timeout in seconds for checking accounts on valid
TIMEOUT = 30

MAJOR_REFS_NUMBER = [10,13] # Сколько рефок на аккаунт major

MAJOR_REFS = { # Сами рефки, коды приглашения
    '374069367',
}
