#!/usr/bin/env python3
"""
Proxy Authentication with Multiple Methods
"""

import time
import subprocess

def extract_proxy_details(proxy):
    """Extract proxy details from any format"""
    try:
        if proxy.startswith('moz-proxy://'):
            # Handle moz-proxy:// format
            clean_proxy = proxy.replace('moz-proxy://', '')
            if '@' in clean_proxy:
                auth_part = clean_proxy.split('@')[0]
                host_part = clean_proxy.split('@')[1]
                username = auth_part.split(':')[0]
                password = auth_part.split(':')[1]
                proxy_ip = host_part.split(':')[0]
                proxy_port = int(host_part.split(':')[1])
            else:
                proxy_ip = clean_proxy.split(':')[0]
                proxy_port = int(clean_proxy.split(':')[1])
                username = password = None
        else:
            # Handle regular format
            if '@' in proxy:
                auth_part = proxy.split('@')[0]
                host_part = proxy.split('@')[1]
                username = auth_part.split(':')[0]
                password = auth_part.split(':')[1]
                proxy_ip = host_part.split(':')[0]
                proxy_port = int(host_part.split(':')[1])
            else:
                proxy_ip = proxy.split(':')[0]
                proxy_port = int(proxy.split(':')[1])
                username = password = None
        
        return username, password, proxy_ip, proxy_port
        
    except Exception as e:
        print(f"❌ Failed to extract proxy details: {e}")
        return None, None, None, None

def setup_proxy_auth(options, proxy, scenario):
    """Set up proxy based on chosen auth method"""
    username, password, proxy_ip, proxy_port = extract_proxy_details(proxy)
    
    if not proxy_ip:
        print("❌ Invalid proxy format")
        return options, username, password
    
    # Set basic proxy settings (always safe)
    options.set_preference('network.proxy.type', 1)
    options.set_preference('network.proxy.http', proxy_ip)
    options.set_preference('network.proxy.http_port', proxy_port)
    options.set_preference('network.proxy.ssl', proxy_ip)
    options.set_preference('network.proxy.ssl_port', proxy_port)
    options.set_preference('network.proxy.share_proxy_settings', True)
    
    auth_method = scenario.get('proxy_auth_method', 'manual')
    
    if auth_method == 'firefox_auto':
        # Use Firefox auto-login
        if username and password:
            options.set_preference('network.proxy.username', username)
            options.set_preference('network.proxy.password', password)
            print("🔐 Using Firefox auto-login")
        else:
            print("⚠️ No credentials for Firefox auto-login")
            
    elif auth_method == 'adb_auto':
        # Don't set username/password - ADB will handle popup
        print("🔐 Using ADB auto-fill (popup will be auto-filled)")
        
    else:  # manual
        # Don't set anything - user will handle popup manually
        print("🔐 Using manual auth")
    
    print(f"🔧 Proxy configured: {proxy_ip}:{proxy_port}")
    return options, username, password

def auto_fill_proxy_auth_with_adb(username, password):
    """Use ADB to auto-fill proxy auth popup with 'Sign in' button"""
    try:
        print("🔄 Auto-filling proxy auth with ADB...")
        
        # Wait for popup to appear
        time.sleep(3)
        
        # Tap username field (top field)
        subprocess.run(['input', 'tap', '500', '350'], check=True)
        time.sleep(0.5)
        
        # Clear field and type username
        subprocess.run(['input', 'keyevent', 'KEYCODE_MOVE_END'], check=True)
        subprocess.run(['input', 'keyevent', 'KEYCODE_SHIFT_LEFT'], check=True)
        subprocess.run(['input', 'keyevent', 'KEYCODE_MOVE_HOME'], check=True)
        subprocess.run(['input', 'keyevent', 'KEYCODE_DEL'], check=True)
        subprocess.run(['input', 'text', username], check=True)
        time.sleep(0.5)
        
        # Tap password field (middle field)
        subprocess.run(['input', 'tap', '500', '450'], check=True)
        time.sleep(0.5)
        
        # Clear field and type password
        subprocess.run(['input', 'keyevent', 'KEYCODE_MOVE_END'], check=True)
        subprocess.run(['input', 'keyevent', 'KEYCODE_SHIFT_LEFT'], check=True)
        subprocess.run(['input', 'keyevent', 'KEYCODE_MOVE_HOME'], check=True)
        subprocess.run(['input', 'keyevent', 'KEYCODE_DEL'], check=True)
        subprocess.run(['input', 'text', password], check=True)
        time.sleep(0.5)
        
        # Tap "Sign in" button (bottom button - adjusted for "Sign in")
        subprocess.run(['input', 'tap', '700', '550'], check=True)  # Right side for "Sign in"
        
        print("✅ Proxy auth auto-filled with 'Sign in' button")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ ADB auto-fill failed: {e}")
        return False
    except Exception as e:
        print(f"❌ ADB auto-fill error: {e}")
        return False

def handle_proxy_auth(driver, proxy, scenario):
    """Handle proxy authentication based on chosen method"""
    auth_method = scenario.get('proxy_auth_method', 'manual')
    
    if auth_method == 'adb_auto':
        username, password, _, _ = extract_proxy_details(proxy)
        if username and password:
            return auto_fill_proxy_auth_with_adb(username, password)
        else:
            print("❌ No credentials for ADB auto-fill")
            return False
            
    elif auth_method == 'manual':
        print("⏳ Manual proxy auth required...")
        print("   Please enter credentials in the Firefox popup")
        input("   Press Enter AFTER completing proxy authentication...")
        return True
        
    else:  # firefox_auto
        # Nothing to do - Firefox handles it automatically
        return True
