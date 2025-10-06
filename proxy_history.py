#!/usr/bin/env python3
"""
Standalone proxy history viewer
Usage: python proxy_history.py
"""

from proxy_manager import ProxyManager

def main():
    print("📋 PROXY USAGE HISTORY")
    print("=" * 50)
    
    proxy_mgr = ProxyManager()
    proxy_mgr.show_proxy_history(50)  # Show last 50 records
    proxy_mgr.show_proxy_stats()      # Show performance stats

if __name__ == "__main__":
    main()
