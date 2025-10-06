#!/usr/bin/env python3
import requests

# Import your ProxyManager class here (copy the entire class code above)

def test_proxy_manager():
    # Initialize proxy manager
    pm = ProxyManager()
    
    # Show initial status
    pm.show_proxy_status()
    
    # Test getting a proxy
    proxy = pm.get_unique_proxy()
    if proxy:
        print(f"\n🎯 Selected Proxy: {proxy}")
        
        # Test the proxy with a request
        try:
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            
            response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
            print(f"✅ Proxy test successful: {response.json()}")
            
            # Mark as successfully used
            pm.mark_proxy_used(proxy, account_number=1, status='success', reason="Test successful")
            
        except Exception as e:
            print(f"❌ Proxy test failed: {e}")
            pm.mark_proxy_used(proxy, account_number=1, status='failed', reason=str(e))
    
    # Show final status
    pm.show_proxy_status()
    pm.show_proxy_history(5)

if __name__ == "__main__":
    test_proxy_manager()
