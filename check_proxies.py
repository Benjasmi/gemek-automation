#!/usr/bin/env python3
"""
Standalone proxy status checker
Usage: python check_proxies.py
"""

from proxy_manager import ProxyManager

def main():
    print("🔍 PROXY STATUS CHECK")
    print("=" * 50)
    
    proxy_mgr = ProxyManager()
    proxy_mgr.show_proxy_status()

if __name__ == "__main__":
    main()
