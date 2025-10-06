#!/usr/bin/env python3
import json
import random
import os
import time
from datetime import datetime

class ProxyManager:
    def __init__(self, proxy_file='proxies.txt', state_file='proxy_state.json', history_file='proxy_history.json'):
        self.proxy_file = proxy_file
        self.state_file = state_file
        self.history_file = history_file
        self.proxies = []
        self.available_proxies = []
        self.load_proxies()
        self.load_proxy_state()
        self.load_proxy_history()
    
    def load_proxy_history(self):
        """Load proxy usage history"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
                print(f"✅ Loaded proxy history: {len(self.history.get('usage_log', []))} records")
            else:
                self.history = {
                    'usage_log': [],
                    'proxy_stats': {},
                    'total_uses': 0,
                    'successful_uses': 0,
                    'failed_uses': 0
                }
                print("✅ Created new proxy history")
        except Exception as e:
            print(f"❌ Failed to load proxy history: {e}")
            self.history = {
                'usage_log': [],
                'proxy_stats': {},
                'total_uses': 0,
                'successful_uses': 0,
                'failed_uses': 0
            }
    
    def save_proxy_history(self):
        """Save proxy usage history"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"❌ Failed to save proxy history: {e}")
    
    def log_proxy_usage(self, proxy, account_number, status, reason=""):
        """Log proxy usage to history"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ip_port = self.extract_ip_port(proxy)
            
            usage_record = {
                'timestamp': timestamp,
                'proxy': ip_port,
                'full_proxy': proxy,
                'account_number': account_number,
                'status': status,  # 'success', 'failed', 'blocked'
                'reason': reason
            }
            
            # Add to usage log
            self.history['usage_log'].append(usage_record)
            
            # Update proxy statistics
            if ip_port not in self.history['proxy_stats']:
                self.history['proxy_stats'][ip_port] = {
                    'total_uses': 0,
                    'successful_uses': 0,
                    'failed_uses': 0,
                    'first_used': timestamp,
                    'last_used': timestamp
                }
            
            stats = self.history['proxy_stats'][ip_port]
            stats['total_uses'] += 1
            stats['last_used'] = timestamp
            
            if status == 'success':
                stats['successful_uses'] += 1
                self.history['successful_uses'] += 1
            else:
                stats['failed_uses'] += 1
                self.history['failed_uses'] += 1
            
            self.history['total_uses'] += 1
            self.save_proxy_history()
            
            print(f"📝 Logged proxy usage: {ip_port} for account #{account_number} - {status}")
            
        except Exception as e:
            print(f"❌ Failed to log proxy usage: {e}")
    
    def load_proxy_state(self):
        """Load used proxies from previous sessions"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    used_proxies = state.get('used_proxies', [])
                    
                    # Mark proxies as used based on saved state
                    for proxy in self.proxies:
                        if proxy['proxy'] in used_proxies:
                            proxy['used'] = True
                    
                    self.available_proxies = [p for p in self.proxies if not p['used']]
                    print(f"✅ Loaded proxy state: {len(used_proxies)} used, {len(self.available_proxies)} available")
        except Exception as e:
            print(f"❌ Failed to load proxy state: {e}")
    
    def save_proxy_state(self):
        """Save used proxies to file"""
        try:
            used_proxies = [p['proxy'] for p in self.proxies if p['used']]
            state = {'used_proxies': used_proxies}
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"❌ Failed to save proxy state: {e}")
    
    def mark_proxy_used(self, proxy, account_number, status='success', reason=""):
        """Mark proxy as used and log to history"""
        for i, p in enumerate(self.proxies):
            if p['proxy'] == proxy:
                self.proxies[i]['used'] = True
                self.available_proxies = [p for p in self.proxies if not p['used']]
                ip_display = self.extract_ip_port(proxy)
                print(f"✅ MARKED AS USED: {ip_display} for account #{account_number} - {status}")
                
                # Log to history
                self.log_proxy_usage(proxy, account_number, status, reason)
                self.save_proxy_state()
                return True
        return False
    
    def extract_ip_port(self, proxy):
        """Extract IP:PORT for display"""
        if '@' in proxy:
            return proxy.split('@')[1]
        return proxy
    
    def get_usage_stats(self):
        """Get current usage statistics"""
        used = len([p for p in self.proxies if p['used']])
        available = len(self.available_proxies)
        total = len(self.proxies)
        return {'used': used, 'available': available, 'total': total}
    
    def get_unique_proxy(self):
        """Get random available proxy"""
        if not self.available_proxies:
            print("❌ No available proxies left!")
            return None
        
        proxy = random.choice(self.available_proxies)
        return proxy['proxy']
    
    def load_proxies(self):
        """Load proxies from file"""
        try:
            with open(self.proxy_file, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
                self.proxies = [{'proxy': line, 'used': False} for line in lines]
                self.available_proxies = self.proxies.copy()
                print(f"✅ Loaded {len(self.proxies)} proxies from {self.proxy_file}")
        except Exception as e:
            print(f"❌ Failed to load proxies: {e}")
    
    def show_proxy_status(self):
        """Show detailed proxy status"""
        stats = self.get_usage_stats()
        history_stats = self.history
        
        print(f"\n📊 CURRENT PROXY STATUS:")
        print(f"   Total Proxies: {stats['total']}")
        print(f"   ✅ Available: {stats['available']}") 
        print(f"   ❌ Used: {stats['used']}")
        
        print(f"\n📈 PROXY HISTORY STATS:")
        print(f"   Total Uses: {history_stats['total_uses']}")
        print(f"   Successful: {history_stats['successful_uses']}")
        print(f"   Failed: {history_stats['failed_uses']}")
        
        # Show used proxies
        used_proxies = [p for p in self.proxies if p['used']]
        if used_proxies:
            print(f"\n❌ CURRENTLY USED PROXIES:")
            for proxy in used_proxies:
                ip_port = self.extract_ip_port(proxy['proxy'])
                proxy_stats = self.history['proxy_stats'].get(ip_port, {})
                success_rate = (proxy_stats.get('successful_uses', 0) / proxy_stats.get('total_uses', 1)) * 100
                print(f"   - {ip_port} (Success: {success_rate:.1f}%)")
    
    def show_proxy_history(self, limit=20):
        """Show detailed proxy usage history"""
        usage_log = self.history.get('usage_log', [])
        
        print(f"\n📋 PROXY USAGE HISTORY (Last {min(limit, len(usage_log))} records):")
        print("=" * 80)
        
        for record in list(reversed(usage_log))[:limit]:
            status_color = "✅" if record['status'] == 'success' else "❌"
            print(f"{status_color} {record['timestamp']} | Account #{record['account_number']} | {record['proxy']} | {record['status'].upper()}")
            if record['reason']:
                print(f"   Reason: {record['reason']}")
        
        print("=" * 80)
    
    def show_proxy_stats(self):
        """Show statistics for each proxy"""
        proxy_stats = self.history.get('proxy_stats', {})
        
        print(f"\n📊 PROXY PERFORMANCE STATS:")
        print("=" * 60)
        
        for ip_port, stats in sorted(proxy_stats.items(), key=lambda x: x[1]['total_uses'], reverse=True):
            total = stats['total_uses']
            success = stats['successful_uses']
            fail = stats['failed_uses']
            success_rate = (success / total) * 100 if total > 0 else 0
            
            print(f"🔸 {ip_port}")
            print(f"   Uses: {total} | Success: {success} | Fail: {fail} | Rate: {success_rate:.1f}%")
            print(f"   First: {stats['first_used']} | Last: {stats['last_used']}")
            print()
    
    def reset_proxies(self):
        """Reset all proxies to available (does NOT clear history)"""
        for proxy in self.proxies:
            proxy['used'] = False
        self.available_proxies = self.proxies.copy()
        self.save_proxy_state()
        print("🔄 All proxies reset to available (history preserved)")
    
    def clear_proxy_history(self):
        """Clear all proxy history"""
        self.history = {
            'usage_log': [],
            'proxy_stats': {},
            'total_uses': 0,
            'successful_uses': 0,
            'failed_uses': 0
        }
        self.save_proxy_history()
        print("🗑️  All proxy history cleared")
