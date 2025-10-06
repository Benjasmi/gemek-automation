#!/usr/bin/env python3
import json
import random
import time
import sys
import os
import glob
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from proxy_manager import ProxyManager
from scenario_runner import ScenarioRunner
from proxy_auth import setup_proxy_auth, handle_proxy_auth, extract_proxy_details
from ip_monitor import IPMonitor
from popup_handler import PopupHandler
from devices import DeviceManager
from data.name_pool import FIRST_NAMES, LAST_NAMES
from data.domain_pool import EMAIL_DOMAINS
from data.timezone_pool import TIMEZONE_REGIONS

class GemekAutomation:
    def __init__(self, config_file="config.json"):
        self.load_config(config_file)
        self.proxy_manager = ProxyManager()
        self.scenario_runner = ScenarioRunner(config_file)
        self.device_manager = DeviceManager()
        self.setup_screenshot_folder()
        self.ip_monitor = IPMonitor(self.proxy_manager)
        
    def setup_screenshot_folder(self):
        """Create screenshots folder if it doesn't exist"""
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        print("📁 Screenshots will be saved in /screenshots/ folder")
        
    def take_screenshot(self, name):
        """Take screenshot and save to screenshots folder"""
        filename = f"screenshots/{name}_{int(time.time())}.png"
        try:
            self.driver.save_screenshot(filename)
            print(f"📸 Screenshot saved: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Failed to take screenshot: {e}")
            return None
        
    def load_config(self, config_file):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
    
    def detect_region_from_ip(self, proxy_ip):
        """Detect broad region from proxy IP for timezone matching"""
        ip_prefix = proxy_ip.split('.')[0]
        
        region_map = {
            'us': ['66', '67', '68', '69', '70', '71', '72', '73', '74', '75', '76', '96', '97', '98', '99', '104', '107', '108', '131', '132', '134', '135', '136', '137', '138', '139', '140', '142', '143', '144', '146', '147', '148', '149', '150', '152', '153', '154', '155', '156', '157', '158', '159', '160', '161', '162', '163', '164', '165', '166', '167', '168', '169', '170', '172', '173', '174', '192', '198', '199', '204', '205', '206', '207', '208', '209', '216'],
            'eu': ['77', '78', '79', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89', '90', '91', '92', '93', '94', '95', '176', '177', '178', '185', '188', '193', '194', '195', '212', '213', '217'],
            'asia': ['1', '14', '27', '36', '39', '42', '43', '49', '58', '59', '60', '61', '101', '103', '106', '110', '111', '112', '113', '114', '115', '116', '117', '118', '119', '120', '121', '122', '123', '124', '125', '126', '175', '180', '182', '183', '202', '203', '210', '211', '218', '219', '220', '221', '222']
        }
        
        for region, prefixes in region_map.items():
            if ip_prefix in prefixes:
                return region
        return "us"
        
    def setup_driver(self, proxy=None, headless_mode=False, device_type="mobile"):
        options = Options()
        
        if headless_mode:
            options.add_argument("--headless")
            print("🔧 Running in HEADLESS mode")
        else:
            print("🔧 Running in VISIBLE mode")
        
        device = self.device_manager.get_random_device(device_type)
        options.set_preference("general.useragent.override", device['user_agent'])
        viewport = device['viewport'].split('x')
        viewport_width = int(viewport[0])
        viewport_height = int(viewport[1])
        
        if self.scenario.get('stealth'):
            stealth = self.scenario['stealth']
            if stealth.get('clear_cookies', True):
                options.set_preference("network.cookie.cookieBehavior", 2)
        
        options.set_preference("network.http.use-cache", False)
        options.set_preference("network.ssl.errorReporting.enabled", False)
        
        if proxy:
            print(f"🔧 Raw proxy received: {proxy}")
            options, username, password = setup_proxy_auth(options, proxy, self.scenario)
            
            if '@' in proxy:
                clean_proxy = proxy.split('@')[1]
            else:
                clean_proxy = proxy
                
            proxy_ip = clean_proxy.split(':')[0]
            proxy_port = int(clean_proxy.split(':')[1])
            
            region = self.detect_region_from_ip(proxy_ip)
            timezone_options = TIMEZONE_REGIONS.get(region, TIMEZONE_REGIONS["us"])
            timezone = random.choice(timezone_options)["timezone"]
            options.set_preference("privacy.timesources.timezone", timezone)
            print(f"🌍 Auto timezone: {timezone} for IP region: {region}")
            
            print(f"🔧 Proxy configured: {proxy_ip}:{proxy_port}")
        
        firefox_binary = "/data/data/com.termux/files/usr/lib/firefox/firefox"
        geckodriver_path = "/data/data/com.termux/files/usr/bin/geckodriver"
        
        options.binary_location = firefox_binary
        service = Service(executable_path=geckodriver_path)
        
        self.driver = webdriver.Firefox(service=service, options=options)
        self.driver.set_page_load_timeout(45)
        self.driver.set_window_size(viewport_width, viewport_height)
        
        return self.driver
        
    def get_proxy(self):
        """Get unique proxy with usage tracking"""
        proxy = self.proxy_manager.get_unique_proxy()
        if proxy:
            return proxy
        else:
            print("❌ No working proxies available in proxy manager!")
            return None
                
    def random_delay(self, min_sec=None, max_sec=None):
        """Random delay with scenario-based timing"""
        if min_sec is None:
            min_sec = self.config['defaults']['min_delay']
        if max_sec is None:
            max_sec = self.config['defaults']['max_delay']
        
        if self.scenario.get('stealth') and self.scenario['stealth'].get('random_delays', True):
            delay = random.uniform(min_sec, max_sec)
            time.sleep(delay)
        else:
            time.sleep(random.uniform(min_sec, max_sec))
    
    def generate_email(self):
        """Better email generation using name/domain pools"""
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        domain = random.choice(EMAIL_DOMAINS)
        number = random.randint(10, 9999)
        
        email_formats = [
            f"{first_name}{last_name}{number}",
            f"{first_name}.{last_name}{number}",
            f"{first_name}{number}",
            f"{last_name}{first_name}{number}",
            f"{first_name}_{last_name}_{number}",
            f"{first_name[0]}{last_name}{number}",
            f"{first_name}.{last_name[0]}{number}",
        ]
        
        email = f"{random.choice(email_formats)}@{domain}"
        print(f"📧 Generated email: {email}")
        return email
        
    def sign_up(self, driver, email, account_number):
        """Robust sign up process with continuous IP monitoring"""
        try:
            print("📝 Starting sign-up...")
            site_config = self.scenario['site']
            print(f"🌐 Loading: {site_config['url']}")
            
            if hasattr(self, 'current_proxy'):
                auth_success = handle_proxy_auth(driver, self.current_proxy, self.scenario)
                if not auth_success:
                    print("❌ Proxy authentication failed")
                    return "failed"
            
            driver.get(site_config['url'])
            print("✅ Page loaded successfully")
            
            if self.ip_monitor.detect_block_instant(driver):
                print("❌ IP BLOCKED on page load")
                self.proxy_manager.mark_proxy_used(self.current_proxy, account_number, 'blocked', 'IP blocked on page load')
                return "ip_used"
            
            self.random_delay(3, 5)
            
            WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "input"))
            )
            
            inputs = driver.find_elements(By.TAG_NAME, "input")
            print(f"Found {len(inputs)} input fields")
            
            for input_field in inputs:
                input_type = input_field.get_attribute("type") or ""
                input_name = input_field.get_attribute("name") or ""
                input_placeholder = input_field.get_attribute("placeholder") or ""
                
                self.random_delay(0.5, 1.5)
                
                if any(x in input_type.lower() + input_name.lower() + input_placeholder.lower() for x in ['email', 'mail']):
                    input_field.send_keys(email)
                    print(f"✅ Filled email: {email}")
                    
                elif "password" in input_type.lower() or "password" in input_name.lower():
                    input_field.send_keys("TestPass123!")
                    print("✅ Filled password")
                    
                elif "confirm" in input_name.lower() or "reenter" in input_placeholder.lower():
                    input_field.send_keys("TestPass123!")
                    print("✅ Filled confirm password")
            
            self.random_delay(2, 4)
            
            print("📜 Scrolling down...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.random_delay(2, 3)
            
            self.take_screenshot("signup_page")
            
            print("🔍 Looking for sign-up button...")
            
            if self.ip_monitor.detect_block_instant(driver):
                print("❌ IP BLOCKED during form filling")
                self.proxy_manager.mark_proxy_used(self.current_proxy, account_number, 'blocked', 'IP blocked during form filling')
                return "ip_used"
            
            signup_texts = ['Sign up', 'Sign Up', 'sign up', 'Register', 'Join', 'Create Account', 'Submit']
            for text in signup_texts:
                popup_handler = PopupHandler(driver, self.take_screenshot)
                if popup_handler.find_and_click_element(text, "signup button", timeout=2):
                    print("🔄 Sign-up clicked - Starting continuous IP monitoring...")
                    
                    if self.ip_monitor.detect_block_continuous(driver, 15):
                        print("❌ IP BLOCKED after sign-up submission")
                        self.proxy_manager.mark_proxy_used(self.current_proxy, account_number, 'blocked', 'IP blocked after sign-up')
                        return "ip_used"
                    
                    current_url = driver.current_url
                    if "register" in current_url or "signup" in current_url:
                        print("❌ Still on registration page - sign-up likely failed")
                        self.take_screenshot("signup_failed")
                        return "failed"
                    
                    print("✅ Sign-up successful - No IP blocks detected")
                    return "success"
            
            print("❌ Could not find or click the sign-up button")
            self.take_screenshot("no_signup_button")
            return "failed"
            
        except Exception as e:
            print(f"❌ Sign-up failed: {e}")
            self.take_screenshot("signup_error")
            import traceback
            traceback.print_exc()
            return "failed"

    def handle_popups(self, driver, account_number):
        """Use PopupHandler for popups"""
        popup_handler = PopupHandler(driver, self.take_screenshot)
        return popup_handler.handle_popups(account_number)
            
    def claim_task(self, driver):
        """Use PopupHandler for task claiming"""
        popup_handler = PopupHandler(driver, self.take_screenshot)
        return popup_handler.claim_task(self.scenario, self.take_screenshot)
            
    def run_account_creation(self, account_number):
        """Run account creation for one account"""
        print("\n" + "=" * 50)
        print(f"👤 Account #{account_number}")
        print("=" * 50)
        
        max_retries = 5
        retry_count = 0
        self.current_proxy = None
        
        while retry_count < max_retries:
            stats = self.proxy_manager.get_usage_stats()
            print(f"📊 Proxies: Available {stats['available']} | Used {stats['used']} | Total {stats['total']}")
            
            proxy = self.get_proxy()
            if not proxy:
                print("❌ No proxies available!")
                return False
                
            self.current_proxy = proxy
            print(f"🔧 Using proxy: {self.proxy_manager.extract_ip_port(proxy)}")
            
            # FIXED: Get device type directly from scenario instead of user_agent
            device_type = self.scenario['device']['id']  # 'mobile', 'android', 'iphone', 'desktop', 'random'
            
            driver = self.setup_driver(
                proxy=proxy, 
                headless_mode=self.scenario['headless_mode'],
                device_type=device_type
            )
            
            try:
                email = self.generate_email()
                signup_result = self.sign_up(driver, email, account_number)
                
                if signup_result == "ip_used":
                    print("🔄 IP already used - trying next proxy")
                    retry_count += 1
                    continue
                    
                elif signup_result == "success":
                    print("✅ Sign-up successful")
                    self.proxy_manager.mark_proxy_used(self.current_proxy, account_number, 'success', 'Account created successfully')
                    
                    popup_success = self.handle_popups(driver, account_number)
                    
                    if popup_success:
                        if self.claim_task(driver):
                            print(f"✅ Account #{account_number} completed successfully")
                            return True
                        else:
                            print(f"⚠️ Account #{account_number} created but task claim failed")
                            return True
                    else:
                        print(f"⚠️ Account #{account_number} created but popup handling failed")
                        return True
                        
                else:
                    print(f"❌ Account #{account_number} failed during sign-up")
                    self.proxy_manager.mark_proxy_used(self.current_proxy, account_number, 'failed', 'Sign-up process failed')
                    return False
                    
            except Exception as e:
                print(f"❌ Error in account #{account_number}: {e}")
                self.proxy_manager.mark_proxy_used(self.current_proxy, account_number, 'failed', f'Error: {str(e)}')
                return False
            finally:
                driver.quit()
                self.random_delay(10, 20)
        
        print(f"❌ Account #{account_number} failed after {max_retries} proxy retries")
        return False
            
    def run(self, scenario):
        """Main automation runner"""
        self.scenario = scenario
        print("🚀 Starting Gemek Automation")
        print("=" * 50)
        print(f"📊 Running scenario: {self.scenario['task']['name']}")
        print(f"📱 Device Category: {self.scenario['device']['name']}")
        print(f"🌍 Location: {self.scenario['location']['name']}")
        print(f"🔗 Proxy: {self.scenario['proxy']['name']}")
        print(f"🔐 IP Auth: {'Yes' if self.scenario['ip_auth'] else 'No'}")
        print(f"⌨️  Auth Mode: {'Auto-fill' if self.scenario['auth_mode'] == 'auto' else 'Manual input'}")
        print(f"🔐 Proxy Auth: {self.scenario['proxy_auth_method'].replace('_', ' ').title()}")
        print("=" * 50)
        
        self.proxy_manager.show_proxy_status()
        print()
        
        successful_accounts = 0
        
        for i in range(1, self.scenario['accounts_count'] + 1):
            if self.run_account_creation(i):
                successful_accounts += 1
        
        stats = self.proxy_manager.get_usage_stats()
        print(f"\n📊 Final Proxy Stats: Available {stats['available']} | Used {stats['used']} | Total {stats['total']}")
        print(f"🎉 Automation completed!")
        print(f"✅ Successful accounts: {successful_accounts}/{self.scenario['accounts_count']}")
        
        self.proxy_manager.show_proxy_status()

if __name__ == "__main__":
    runner = ScenarioRunner()
    scenario = runner.run_interactive_setup()
    
    automation = GemekAutomation()
    automation.run(scenario)
