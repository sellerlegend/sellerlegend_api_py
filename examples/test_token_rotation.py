#!/usr/bin/env python3
"""
Test OAuth token rotation behavior after fixes.

Expected behavior with fixed listeners:
1. When refreshing tokens, old refresh token should be revoked for same user/client
2. Only ONE valid refresh token should exist per user/client
3. Old access tokens should be revoked for same user/client
4. Other users' tokens should remain unaffected
"""

from dotenv import load_dotenv
from pathlib import Path
import os
import time
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from sellerlegend_api import SellerLegendClient, AuthenticationError

load_dotenv(".env")

CLIENT_ID = os.getenv("SELLERLEGEND_CLIENT_ID")
CLIENT_SECRET = os.getenv("SELLERLEGEND_CLIENT_SECRET")
BASE_URL = os.getenv("SELLERLEGEND_BASE_URL", "https://app.sellerlegend.com")
ACCESS_TOKEN = os.getenv("SELLERLEGEND_ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("SELLERLEGEND_REFRESH_TOKEN")

def test_token_rotation():
    """Test OAuth token rotation behavior."""

    print("=" * 60)
    print("Testing OAuth Token Rotation Behavior")
    print("=" * 60)

    # Initialize client with existing tokens
    client = SellerLegendClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        base_url=BASE_URL,
        access_token=ACCESS_TOKEN,
        refresh_token=REFRESH_TOKEN
    )

    print("\n1. Testing initial authentication with existing tokens...")
    try:
        user_info = client.user.get_me()
        print(f"   ✅ Successfully authenticated as: {user_info['user'].get('name', 'Unknown')}")
        print(f"   User ID: {user_info['user'].get('id')}")
    except Exception as e:
        print(f"   ❌ Failed to authenticate with existing tokens: {e}")
        return

    print("\n2. Storing original tokens...")
    original_access = ACCESS_TOKEN
    original_refresh = REFRESH_TOKEN
    print(f"   Original Access Token: {original_access[:20]}...")
    print(f"   Original Refresh Token: {original_refresh[:20]}...")

    print("\n3. Refreshing tokens (first refresh)...")
    try:
        token_data_1 = client.refresh_token()
        new_access_1 = token_data_1['access_token']
        new_refresh_1 = token_data_1['refresh_token']
        print(f"   ✅ First refresh successful")
        print(f"   New Access Token: {new_access_1[:20]}...")
        print(f"   New Refresh Token: {new_refresh_1[:20]}...")
    except Exception as e:
        print(f"   ❌ First refresh failed: {e}")
        return

    print("\n4. Testing if old refresh token still works...")
    # Create a new client with the OLD refresh token
    old_token_client = SellerLegendClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        base_url=BASE_URL,
        access_token=original_access,
        refresh_token=original_refresh
    )

    try:
        old_token_client.refresh_token()
        print(f"   ❌ ISSUE: Old refresh token still works! (Should be revoked)")
        print(f"      This indicates PruneOldTokens may not be working correctly")
    except AuthenticationError as e:
        print(f"   ✅ Old refresh token correctly revoked: {e}")
    except Exception as e:
        print(f"   ⚠️  Unexpected error: {e}")

    print("\n5. Testing if new refresh token works (second refresh)...")
    # Update client with new tokens
    client._oauth_client.access_token = new_access_1
    client._oauth_client.refresh_token = new_refresh_1

    try:
        token_data_2 = client.refresh_token()
        new_access_2 = token_data_2['access_token']
        new_refresh_2 = token_data_2['refresh_token']
        print(f"   ✅ Second refresh successful")
        print(f"   New Access Token: {new_access_2[:20]}...")
        print(f"   New Refresh Token: {new_refresh_2[:20]}...")
    except Exception as e:
        print(f"   ❌ Second refresh failed: {e}")
        return

    print("\n6. Testing if first refresh token still works...")
    # Try using the first refresh token
    first_refresh_client = SellerLegendClient(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        base_url=BASE_URL,
        access_token=new_access_1,
        refresh_token=new_refresh_1
    )

    try:
        first_refresh_client.refresh_token()
        print(f"   ❌ ISSUE: First refresh token still works! (Should be revoked)")
        print(f"      This indicates PruneOldTokens may not be working correctly")
    except AuthenticationError as e:
        print(f"   ✅ First refresh token correctly revoked: {e}")
    except Exception as e:
        print(f"   ⚠️  Unexpected error: {e}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("\nExpected behavior (with fixes):")
    print("  • Only ONE refresh token should be valid per user/client")
    print("  • Old refresh tokens should be revoked when new ones are issued")
    print("  • This prevents token accumulation and ensures proper rotation")

    print("\nIf old refresh tokens still work, check:")
    print("  1. PruneOldTokens listener is enabled in EventServiceProvider")
    print("  2. PruneOldTokens correctly filters by user_id and client_id")
    print("  3. Database queries are executing properly in production")

    # Save the latest working tokens back to .env for future use
    print("\n7. Update .env with latest tokens...")
    print(f"SELLERLEGEND_ACCESS_TOKEN={new_access_2}")
    print(f"SELLERLEGEND_REFRESH_TOKEN={new_refresh_2}")


if __name__ == "__main__":
    try:
        test_token_rotation()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)