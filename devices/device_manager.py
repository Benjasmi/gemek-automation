#!/usr/bin/env python3
import random
from .android_pool import ANDROID_DEVICES
from .iphone_pool import IPHONE_DEVICES
from .desktop_pool import DESKTOP_DEVICES

class DeviceManager:
    def __init__(self):
        self.used_devices = []
        self.all_devices = self._load_all_devices()
    
    def _load_all_devices(self):
        """Combine all devices into one list"""
        all_devices = []
        
        # Add Android devices
        for brand_devices in ANDROID_DEVICES.values():
            all_devices.extend(brand_devices)
        
        # Add iPhone devices
        all_devices.extend(IPHONE_DEVICES)
        
        # Add Desktop devices
        for os_devices in DESKTOP_DEVICES.values():
            all_devices.extend(os_devices)
        
        print(f"📱 Loaded {len(all_devices)} total devices")
        return all_devices
    
    def get_random_device(self, category="random"):
        """Get random device with no repetition"""
        if category == "android":
            available = self._get_available_devices(self._get_android_devices())
        elif category == "iphone":
            available = self._get_available_devices(IPHONE_DEVICES)
        elif category == "desktop":
            available = self._get_available_devices(self._get_desktop_devices())
        else:  # random
            available = self._get_available_devices(self.all_devices)
        
        if not available:
            # Reset if no unique devices left
            self.used_devices = []
            available = self.all_devices
        
        device = random.choice(available)
        self.used_devices.append(device['name'])
        
        print(f"📱 Selected: {device['name']}")
        return device
    
    def _get_available_devices(self, device_list):
        """Get devices not yet used"""
        return [d for d in device_list if d['name'] not in self.used_devices]
    
    def _get_android_devices(self):
        """Get all Android devices"""
        android_devices = []
        for brand_devices in ANDROID_DEVICES.values():
            android_devices.extend(brand_devices)
        return android_devices
    
    def _get_desktop_devices(self):
        """Get all Desktop devices"""
        desktop_devices = []
        for os_devices in DESKTOP_DEVICES.values():
            desktop_devices.extend(os_devices)
        return desktop_devices
    
    def get_device_count(self):
        """Get total device count"""
        return len(self.all_devices)
    
    def reset_used_devices(self):
        """Reset used devices tracking"""
        self.used_devices = []
        print("🔄 Device usage tracking reset")
