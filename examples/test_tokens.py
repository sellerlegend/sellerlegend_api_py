import os
import sys
from pathlib import Path
from dotenv import load_dotenv


sys.path.insert(0, str(Path(__file__).parent.parent))
from sellerlegend_api import SellerLegendClient, AuthenticationError

load_dotenv(".env")

CLIENT_ID = os.getenv("SELLERLEGEND_CLIENT_ID")
CLIENT_SECRET = os.getenv("SELLERLEGEND_CLIENT_SECRET")
BASE_URL = os.getenv("SELLERLEGEND_BASE_URL", "https://app.sellerlegend.com")
ACCESS_TOKEN = os.getenv("SELLERLEGEND_ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("SELLERLEGEND_REFRESH_TOKEN")

client = SellerLegendClient(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    base_url=BASE_URL,
    access_token=ACCESS_TOKEN,
    refresh_token=REFRESH_TOKEN
)

print(client.user.get_me())
