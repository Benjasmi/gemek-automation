#!/usr/bin/env python3
"""
Popup Handler - Handles ALL popups, chest animations, and element clicking
"""

import time
import subprocess
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

class PopupHandler:
    def __init__(self, driver, take_screenshot_func=None):
        self.driver = driver
        self.take_screenshot = take_screenshot_func
    
    def find_and_click_element(self, text, description, timeout=10):
        """Find and click ANY element with exact text (case insensitive)"""
        try:
            xpath = f"//*[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{text.lower()}']"
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath))
            )
            
            for element in elements:
                try:
                    if element.is_displayed() and element.is_enabled():
                        element.click()
                        print(f"✅ Clicked {description}: '{text}'")
                        return True
                except:
                    continue
                    
            print(f"❌ Could not click {description}: '{text}'")
            return False
            
        except Exception as e:
            print(f"❌ Failed to find {description} '{text}': {e}")
            return False
    
    def close_treasure_chest(self):
        """Close treasure chest popup with multiple fallback methods"""
        print("🎯 Closing treasure chest popup...")
        
        # Method 1: Try common close button selectors (X icons)
        close_selectors = [
            "//button[@aria-label='Close']",
            "//button[contains(@class, 'close')]",
            "//div[contains(@class, 'close')]",
            "//span[contains(@class, 'close')]",
            "//*[contains(@class, 'modal-close')]",
            "//*[contains(@class, 'popup-close')]",
            "//*[contains(@class, 'btn-close')]",
            "//*[text()='×']",  # The X symbol
            "//*[text()='✕']",  # Alternative X symbol
            "//button[contains(text(), 'Close')]",
            "//button[contains(text(), 'close')]",
        ]
        
        for selector in close_selectors:
            try:
                close_btn = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                close_btn.click()
                print(f"✅ Chest closed using selector: {selector}")
                time.sleep(1)
                return True
            except:
                continue
        
        # Method 2: Try clicking common X button positions (top-right area)
        print("🔧 Trying coordinate clicking for X button...")
        coordinate_positions = [
            (350, 150),   # Top-right area (common X position)
            (380, 120),   # Slightly different position
            (400, 100),   # Extreme top-right
            (300, 140),   # Left of top-right
        ]
        
        for x, y in coordinate_positions:
            try:
                actions = ActionChains(self.driver)
                actions.move_by_offset(x, y).click().perform()
                print(f"✅ Chest closed by clicking coordinates ({x}, {y})")
                time.sleep(1)
                
                # Verify popup closed by checking if we can interact with page
                try:
                    body = self.driver.find_element(By.TAG_NAME, "body")
                    body.click()  # Try clicking body to ensure popup is gone
                    return True
                except:
                    continue
                    
            except Exception as e:
                continue
        
        # Method 3: Press ESC key as fallback
        try:
            from selenium.webdriver.common.keys import Keys
            body = self.driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.ESCAPE)
            print("✅ Chest closed by pressing ESC key")
            time.sleep(1)
            return True
        except:
            pass
        
        # Method 4: Click outside popup (background)
        try:
            # Click at a safe position away from popup center
            actions = ActionChains(self.driver)
            actions.move_by_offset(50, 50).click().perform()  # Top-left corner
            print("✅ Chest closed by clicking outside popup")
            time.sleep(1)
            return True
        except:
            pass
        
        print("❌ Could not close treasure chest with any method")
        if self.take_screenshot:
            self.take_screenshot("chest_close_failed")
        return False
    
    def handle_popups(self, account_number):
        """Handle ALL post-signup popups"""
        try:
            print("🎯 Handling post-signup popups...")
            
            if self.take_screenshot:
                self.take_screenshot(f"after_signup_{account_number}")
            
            # Wait for popups to appear
            time.sleep(3)
            
            # POPUP 1: Site Introduction - Click "close"
            print("🔄 Handling Site Introduction popup...")
            if not self.find_and_click_element("close", "site intro close"):
                print("❌ Failed to close site introduction")
                if self.take_screenshot:
                    self.take_screenshot("site_intro_failed")
                return False
            
            time.sleep(2)
            
            # POPUP 2: Treasure Chest - Click "open treasure chest"
            print("🔄 Handling Treasure Chest popup...")
            if not self.find_and_click_element("open treasure chest", "treasure chest"):
                print("❌ Failed to open treasure chest")
                if self.take_screenshot:
                    self.take_screenshot("treasure_chest_failed")
                return False
            
            # Wait for chest animation
            print("⏳ Waiting 6 seconds for chest animation...")
            time.sleep(6)
            
            # Close the treasure chest popup
            if not self.close_treasure_chest():
                print("❌ Failed to close treasure chest")
                if self.take_screenshot:
                    self.take_screenshot("chest_close_failed")
                return False
            
            if self.take_screenshot:
                self.take_screenshot(f"after_popups_{account_number}")
            
            print("✅ All popups handled successfully")
            return True
            
        except Exception as e:
            print(f"❌ Popup handling failed: {e}")
            if self.take_screenshot:
                self.take_screenshot(f"popup_failure_{account_number}")
            return False
    
    def claim_task(self, scenario, take_screenshot_func=None):
        """Claim task with proper scrolling and multi-page handling"""
        task_mode = scenario['task']['id']
        site_config = scenario['site']
        
        if task_mode == "quick_signup":
            print("⏸️ Quick signup mode - skipping task claim")
            return True
            
        if not site_config.get('enable_task_claim', True):
            print("⏸️ Task claiming disabled for this site")
            return True
            
        try:
            print("🎯 Starting task claiming...")
            
            # Scroll down to reveal hidden content
            print("📜 Scrolling down to reveal tasks...")
            self.driver.execute_script("window.scrollBy(0, 300);")
            time.sleep(2)
            
            # Step 1: Find and click "Task" element
            print("🔍 Looking for 'Task' element...")
            if not self.find_and_click_element("Task", "task navigation"):
                print("❌ No task elements found!")
                if take_screenshot_func:
                    take_screenshot_func("task_not_found")
                return False
            
            # Wait for new page to load
            time.sleep(3)
            
            # Step 2: Find and click "To Complete" button on new page
            print("🔍 Looking for 'To Complete' button...")
            if not self.find_and_click_element("To complete", "complete task"):
                # Try alternative text
                if not self.find_and_click_element("complete", "complete task"):
                    print("❌ No complete elements found!")
                    if take_screenshot_func:
                        take_screenshot_func("complete_not_found")
                    return False
            
            # Step 3: Wait for task to complete
            print("⏳ Waiting 7 seconds for task completion...")
            time.sleep(7)
            
            if take_screenshot_func:
                take_screenshot_func("task_completed")
            print("✅ Task claiming process completed")
            return True
            
        except Exception as e:
            print(f"❌ Task claiming failed: {e}")
            if take_screenshot_func:
                take_screenshot_func("task_claim_failed")
            return False
