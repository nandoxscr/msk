from os import getenv
from dotenv import load_dotenv
load_dotenv()

API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
SESSION_STRING = getenv("SESSION_STRING")
OWNER_ID = int(getenv("OWNER_ID", 0))
COOK_PATH = getenv("COOK_PATH")
MAX_DURATION_MINUTES = int(getenv("MAX_DURATION_MINUTES", 20))

sudo_users_str = getenv("SUDO_USERS", "")
SUDO_USERS = [int(x) for x in sudo_users_str.split(',') if x.strip().isdigit()] if sudo_users_str else []


PREFIX = "."
RPREFIX = "$"

# No Need To Edit Below This

LOG_FILE_NAME = "YMusic.txt"
