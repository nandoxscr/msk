from os import getenv
from dotenv import load_dotenv
load_dotenv()

API_ID = int(getenv("API_ID"))
API_HASH = getenv("API_HASH")
SESSION_STRING = getenv("SESSION_STRING")
OWNER_ID = int(getenv("OWNER_ID", 0))
PREFIX = "."
RPREFIX = "$"

# No Need To Edit Below This

LOG_FILE_NAME = "YMusic.txt"
