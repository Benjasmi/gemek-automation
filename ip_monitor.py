#!/usr/bin/env python3
"""
IP Monitor - Handles FAST IP blocking detection with detailed logging
"""

from selenium.webdriver.common.by import By
import time

class IPMonitor:
    def __init__(self, proxy_manager):
        self.proxy_manager = proxy_manager
        self.block_keywords = [
            "ip exceeded", "ip limit", "too many requests", 
            "rate limit", "quota exceeded", "ip used",
            "ip blocked", "maximum accounts", "already registered",
            "exceeded", "limit", "too many", "quota", "restricted"
        ]
    
    def detect_block_continuous(self, driver, check_duration=15):
        """Continuous monitoring with live logging"""
        print(f"👀 STARTING IP MONITORING for {check_duration} seconds...")
        start_time = time.time()
        check_count = 0
        
        while time.time() - start_time < check_duration:
            check_count += 1
            print(f"🔍 Check #{check_count}...")
            
            if self._check_current_page(driver):
                print(f"🚨 IP BLOCK CONFIRMED at {time.time() - start_time:.1f}s")
                return True
            
            time.sleep(0.3)  # Check every 0.3 seconds
        
        print(f"✅ IP MONITORING COMPLETE: No blocks detected in {check_duration}s")
        return False
    
    def _check_current_page(self, driver):
        """Check current page state for IP blocks WITH DEBUG LOGGING"""
        try:
            # Method 1: Check page source
            page_source = driver.page_source.lower()
            for keyword in self.block_keywords:
                if keyword in page_source:
                    print(f"🚨 POPUP DETECTED IN PAGE SOURCE: '{keyword}'")
                    return True
            
            # Method 2: Check visible text in body
            try:
                body = driver.find_element(By.TAG_NAME, "body")
                body_text = body.text.lower()
                for keyword in self.block_keywords:
                    if keyword in body_text:
                        print(f"🚨 POPUP DETECTED IN BODY TEXT: '{keyword}'")
                        return True
            except:
                pass
            
            # Method 3: Check common popup/error elements
            popup_selectors = [
                "//div[contains(@class, 'error')]",
                "//div[contains(@class, 'alert')]",
                "//div[contains(@class, 'message')]",
                "//div[contains(@class, 'notification')]",
                "//div[contains(@class, 'popup')]",
                "//div[contains(@class, 'modal')]",
                "//*[contains(@class, 'error')]",
                "//*[contains(@class, 'alert')]",
                "//*[contains(@class, 'popup')]"
            ]
            
            for selector in popup_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            element_text = element.text.lower()
                            if element_text.strip():  # Only if has text
                                print(f"👀 FOUND POPUP ELEMENT: '{element_text[:50]}...'")
                                for keyword in self.block_keywords:
                                    if keyword in element_text:
                                        print(f"🚨 POPUP DETECTED IN ELEMENT: '{keyword}'")
                                        return True
                except:
                    continue
            
            # Log that we're checking but found nothing
            print("🔍 IP Monitor: No blocks detected this check")
            return False
            
        except Exception as e:
            print(f"⚠️ IP Monitor check error: {e}")
            return False
    
    def detect_block_instant(self, driver):
        """Quick check - for places where we can't do continuous monitoring"""
        return self._check_current_page(driver)
    
    def mark_ip_used(self, proxy):
        """Mark IP as used"""
        if proxy:
            self.proxy_manager.mark_proxy_used(proxy)
            ip_display = self.extract_ip_port(proxy)
            print(f"✅ MARKED IP AS USED: {ip_display}")
    
    def extract_ip_port(self, proxy):
        """Extract IP:PORT from proxy string for display"""
        if '@' in proxy:
            return proxy.split('@')[1]
        return proxy
    
    def handle_ip_block(self, driver, current_proxy):
        """Handle IP block scenario"""
        print("🔄 HANDLING IP BLOCK - Marking proxy as used")
        self.mark_ip_used(current_proxy)
        return "ip_used"
