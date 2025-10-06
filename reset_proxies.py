#!/usr/bin/env python3
"""
Standalone proxy reset tool
Usage: python reset_proxies.py
"""

from proxy_manager import ProxyManager

def main():
    print("🔄 RESETTING ALL PROXIES")
    print("=" * 50)
    
    proxy_mgr = ProxyManager()
    proxy_mgr.reset_proxies()

if __name__ == "__main__":
    main()
