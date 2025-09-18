#!/usr/bin/env python3
"""
Interactive setup script for test configuration with OAuth flow
Saves configuration to .env file in SDK root
"""

import os
import sys
import webbrowser
import time
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add the SDK to path so we can import it
sys.path.insert(0, str(Path(__file__).parent))

from sellerlegend_api import SellerLegendClient
from sellerlegend_api.exceptions import AuthenticationError


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handler for OAuth callback."""
    
    def do_GET(self):
        """Handle GET request from OAuth callback."""
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        
        if 'code' in query_params:
            self.server.auth_code = query_params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            response_html = """
                <html>
                <head><title>Authentication Successful</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: green;">Authentication Successful!</h1>
                    <p>You can now close this window and return to the terminal.</p>
                    <script>setTimeout(function() { window.close(); }, 3000);</script>
                </body>
                </html>
            """
            self.wfile.write(response_html.encode('utf-8'))
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_html = """
                <html>
                <head><title>Authentication Failed</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: red;">Authentication Failed</h1>
                    <p>No authorization code received. Please try again.</p>
                </body>
                </html>
            """
            self.wfile.write(error_html.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


def create_config_interactive():
    """Create configuration file interactively."""
    print("\n" + "="*60)
    print("SellerLegend API Test Configuration Setup")
    print("="*60 + "\n")
    
    config = {}
    
    # Get base URL
    print("Enter the base URL for the SellerLegend API")
    print("(press Enter for default: https://app.sellerlegend.com):")
    base_url = input().strip()
    config['base_url'] = base_url if base_url else "https://app.sellerlegend.com"
    
    # Get OAuth credentials
    print("\nEnter your OAuth Client ID:")
    client_id = input().strip()
    if not client_id:
        print("❌ Client ID is required!")
        return None
    config['client_id'] = client_id
    
    print("\nEnter your OAuth Client Secret:")
    client_secret = input().strip()
    if not client_secret:
        print("❌ Client Secret is required!")
        return None
    config['client_secret'] = client_secret
    
    print("\nEnter the OAuth Redirect URI (must match your app settings)")
    print("(press Enter for default: http://localhost:5001/callback):")
    redirect_uri = input().strip()
    config['redirect_uri'] = redirect_uri if redirect_uri else "http://localhost:5001/callback"
    
    return config


def perform_oauth_flow(config):
    """Perform OAuth authorization code flow to get tokens."""
    print("\n" + "="*60)
    print("Starting OAuth Authorization Flow")
    print("="*60 + "\n")
    
    try:
        # Create client with redirect_uri
        client = SellerLegendClient(
            client_id=config['client_id'],
            client_secret=config['client_secret'],
            base_url=config['base_url'],
            redirect_uri=config.get('redirect_uri', 'http://localhost:5001/callback')
        )
        
        # Generate authorization URL
        auth_url, state = client.get_authorization_url(
            state="test_auth_" + str(int(time.time()))
        )
        
        print(f"Opening browser for authorization...")
        print(f"If browser doesn't open automatically, visit this URL:")
        print(f"\n{auth_url}\n")
        
        # Start local server to capture callback
        server = HTTPServer(('localhost', 5001), OAuthCallbackHandler)
        server.auth_code = None
        server.timeout = 1  # Short timeout for handle_request
        
        # Open browser
        try:
            webbrowser.open(auth_url)
        except:
            print("⚠️ Could not open browser automatically")
        
        # Wait for callback
        print("Waiting for authorization (timeout: 2 minutes)...")
        print("After authorizing in the browser, you'll be redirected back here.\n")
        
        start_time = time.time()
        while server.auth_code is None and (time.time() - start_time) < 120:
            try:
                server.handle_request()
            except KeyboardInterrupt:
                print("\n⚠️ OAuth flow cancelled by user")
                return False
        
        if server.auth_code:
            print(f"✅ Authorization code received!")
            
            # Exchange code for tokens
            print("Exchanging authorization code for tokens...")
            try:
                tokens = client.authenticate_with_code(
                    code=server.auth_code,
                    state=state
                )
                
                config['access_token'] = tokens['access_token']
                if 'refresh_token' in tokens:
                    config['refresh_token'] = tokens['refresh_token']
                
                print("✅ Tokens obtained successfully!")
                
                # Test the tokens
                print("\nTesting tokens by fetching user info...")
                test_client = SellerLegendClient(
                    access_token=tokens['access_token'],
                    base_url=config['base_url']
                )
                
                user_info = test_client.user.get_me()
                if user_info and 'user' in user_info:
                    print(f"✅ Authentication successful! User: {user_info['user'].get('email', 'Unknown')}")
                
                return True
                
            except Exception as e:
                print(f"❌ Failed to exchange code for tokens: {e}")
                return False
        else:
            print("❌ Timeout - no authorization code received")
            print("Make sure to authorize the application in your browser")
            return False
            
    except KeyboardInterrupt:
        print("\n⚠️ OAuth flow interrupted by user")
        return False
    except Exception as e:
        print(f"❌ OAuth flow error: {e}")
        return False


def save_config(config):
    """Save configuration to .env file."""
    env_file = Path.cwd() / '.env'
    
    # Build the .env content
    env_content = []
    env_content.append("# SellerLegend API Configuration")
    env_content.append("# Generated by setup_test_config.py")
    env_content.append("")
    
    # Add configuration values
    if 'base_url' in config:
        env_content.append(f"SELLERLEGEND_BASE_URL={config['base_url']}")
    if 'client_id' in config:
        env_content.append(f"SELLERLEGEND_CLIENT_ID={config['client_id']}")
    if 'client_secret' in config:
        env_content.append(f"SELLERLEGEND_CLIENT_SECRET={config['client_secret']}")
    if 'redirect_uri' in config:
        env_content.append(f"SELLERLEGEND_REDIRECT_URI={config['redirect_uri']}")
    if 'access_token' in config:
        env_content.append(f"SELLERLEGEND_ACCESS_TOKEN={config['access_token']}")
    if 'refresh_token' in config:
        env_content.append(f"SELLERLEGEND_REFRESH_TOKEN={config['refresh_token']}")
    
    # Add optional test data if provided
    if config.get('test_account_id'):
        env_content.append(f"SELLERLEGEND_ACCOUNT_ID={config['test_account_id']}")
    if config.get('test_marketplace_id'):
        env_content.append(f"SELLERLEGEND_MARKETPLACE_ID={config['test_marketplace_id']}")
    if config.get('test_seller_id'):
        env_content.append(f"SELLERLEGEND_SELLER_ID={config['test_seller_id']}")
    if config.get('test_sku'):
        env_content.append(f"SELLERLEGEND_SKU={config['test_sku']}")
    if config.get('test_asin'):
        env_content.append(f"SELLERLEGEND_ASIN={config['test_asin']}")
    
    try:
        with open(env_file, 'w') as f:
            f.write('\n'.join(env_content) + '\n')
        print(f"\n✅ Configuration saved to {env_file}")
        return True
    except Exception as e:
        print(f"❌ Failed to save config: {e}")
        return False


def main():
    """Main entry point."""
    print("\n" + "="*60)
    print("SellerLegend Python SDK - Test Configuration Setup")
    print("="*60)

    # Check if .env already exists
    env_file = Path.cwd() / '.env'
    if env_file.exists():
        print(f"\n⚠️ Configuration file already exists at {env_file}")
        print("Do you want to overwrite it? (y/n): ", end='')
        response = input().strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    # Create configuration interactively
    config = create_config_interactive()
    if not config:
        print("\n❌ Configuration setup failed!")
        sys.exit(1)
    
    # Save initial config (without tokens)
    save_config(config)
    
    # Ask if user wants to perform OAuth flow
    print("\n" + "="*60)
    print("OAuth Authentication")
    print("="*60)
    print("\nDo you want to perform OAuth flow now to get access tokens?")
    print("(You can also add tokens manually to test_config.json later)")
    print("Perform OAuth flow? (y/n): ", end='')
    
    response = input().strip().lower()
    if response == 'y':
        if perform_oauth_flow(config):
            # Save config with tokens
            save_config(config)
            print("\n" + "="*60)
            print("✅ Setup complete! You can now run the integration tests.")
            print("="*60)
        else:
            print("\n⚠️ OAuth flow failed, but config was saved.")
            print("You can add tokens manually to .env file")
    else:
        print("\n" + "="*60)
        print("✅ Configuration saved without tokens.")
        print("Add 'SELLERLEGEND_ACCESS_TOKEN' and 'SELLERLEGEND_REFRESH_TOKEN' to .env file to run tests.")
        print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)