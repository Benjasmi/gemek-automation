#!/usr/bin/env python3
import json
import random

class ScenarioRunner:
    def __init__(self, config_file="config.json"):
        self.load_config(config_file)
        self.scenario = {}
        
    def load_config(self, config_file):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
    
    def ask_question(self, question, options=None, allow_random=False, default=None):
        """Ask interactive question with options"""
        print(f"\n{question}")
        
        if options:
            for i, option in enumerate(options, 1):
                if isinstance(option, dict):
                    name = option.get('name', option.get('id', f'Option {i}'))
                    desc = option.get('description', '')
                    if desc:
                        print(f"  [{i}] {name} - {desc}")
                    else:
                        print(f"  [{i}] {name}")
                else:
                    print(f"  [{i}] {option}")
            
            if allow_random:
                print(f"  [{len(options) + 1}] Random")
        
        if default is not None:
            prompt = f"Choose (1-{len(options) if options else 'N'}) [default: {default}]: "
        else:
            prompt = f"Choose (1-{len(options) if options else 'N'}): "
        
        while True:
            try:
                choice = input(prompt).strip()
                if not choice and default is not None:
                    return default
                
                if options:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(options):
                        return options[choice_num - 1]
                    elif allow_random and choice_num == len(options) + 1:
                        return random.choice(options)
                    else:
                        print(f"Please enter 1-{len(options) + 1 if allow_random else len(options)}")
                else:
                    return choice
                    
            except (ValueError, IndexError):
                print("Please enter a valid number")
    
    def ask_yes_no(self, question, default=None):
        """Ask yes/no question"""
        if default is True:
            prompt = f"{question} (y/n) [default: y]: "
        elif default is False:
            prompt = f"{question} (y/n) [default: n]: "
        else:
            prompt = f"{question} (y/n): "
        
        while True:
            choice = input(prompt).strip().lower()
            if not choice and default is not None:
                return default
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no']:
                return False
            else:
                print("Please enter y or n")
    
    def get_accounts_count(self):
        """Ask for number of accounts"""
        while True:
            try:
                count = input("\nHow many accounts? (1-50) [default: 1]: ").strip()
                if not count:
                    return self.config['defaults']['max_accounts']
                
                count = int(count)
                if 1 <= count <= 50:
                    return count
                else:
                    print("Please enter a number between 1-50")
            except ValueError:
                print("Please enter a valid number")
    
    def get_headless_mode(self):
        """Ask for headless mode"""
        default = self.config['defaults']['default_headless_mode']
        return self.ask_yes_no("Headless mode?", default)
    
    def get_device_scenario(self):
        """Ask for device scenario - UPDATED for new DeviceManager"""
        devices = [
            {"id": "mobile", "name": "Mobile Devices", "description": "Android & iPhone devices"},
            {"id": "android", "name": "Android Only", "description": "100+ Android devices"},
            {"id": "iphone", "name": "iPhone Only", "description": "50+ iPhone devices"},
            {"id": "desktop", "name": "Desktop Only", "description": "40+ Desktop computers"},
            {"id": "random", "name": "Random All", "description": "190+ All device types"}
        ]
        
        choice = self.ask_question(
            "Choose device category:",
            devices,
            allow_random=False,
            default=devices[0]
        )
        return choice
    
    def get_location_scenario(self):
        """Ask for location scenario"""
        locations = self.config['available_options']['locations']
        choice = self.ask_question(
            "Choose location scenario:",
            locations,
            allow_random=True,
            default=locations[0]
        )
        return choice
    
    def get_stealth_scenario(self):
        """Ask for stealth scenario"""
        use_stealth = self.ask_yes_no("Use stealth scenarios?")
        
        if not use_stealth:
            return None
        
        stealth_modes = self.config['available_options']['stealth_modes']
        choice = self.ask_question(
            "Choose stealth mode:",
            stealth_modes,
            allow_random=False,
            default=stealth_modes[0]
        )
        return choice
    
    def get_proxy_scenario(self):
        """Ask for proxy scenario"""
        proxy_modes = self.config['available_options']['proxy_modes']
        choice = self.ask_question(
            "Choose proxy mode:",
            proxy_modes,
            allow_random=False,
            default=proxy_modes[0]
        )
        return choice
    
    def get_task_scenario(self):
        """Ask for task scenario"""
        task_modes = self.config['available_options']['task_modes']
        choice = self.ask_question(
            "Choose task mode:",
            task_modes,
            allow_random=False,
            default=task_modes[0]
        )
        return choice
    
    def get_ip_auth_option(self):
        """Ask for IP authentication option"""
        return self.ask_yes_no("Use IP authentication (no username/password)?", default=True)
    
    def get_auth_mode(self):
        """Ask for authentication mode"""
        print("\n🔐 Authentication Mode:")
        print("  [1] Auto-fill (automatic)")
        print("  [2] Manual input (you type credentials)")
        
        while True:
            choice = input("Choose (1-2) [default: 1]: ").strip()
            if not choice:
                return "auto"
            
            if choice == "1":
                return "auto"
            elif choice == "2":
                return "manual"
            else:
                print("Please enter 1 or 2")
    
    def get_proxy_auth_method(self):
        """Ask for proxy authentication method"""
        print("\n🔐 Proxy Authentication Method:")
        print("  [1] Manual input (default - you enter credentials in Firefox popup)")
        print("  [2] ADB Auto-fill (Termux auto-fills popup)")
        print("  [3] Firefox Auto-login (may not work for all proxies)")
        
        while True:
            choice = input("Choose (1-3) [default: 1]: ").strip()
            if not choice:
                return "manual"
            
            auth_methods = {
                "1": "manual",
                "2": "adb_auto", 
                "3": "firefox_auto"
            }
            
            if choice in auth_methods:
                return auth_methods[choice]
            else:
                print("Please enter 1, 2, or 3")
    
    def get_site_choice(self):
        """Ask for site choice"""
        sites = list(self.config['predefined_sites'].keys())
        site_options = [{"id": "predefined", "name": f"Predefined ({self.config['predefined_sites']['gemek']['name']})"}] + [{"id": "custom", "name": "Custom URL"}]
        
        choice = self.ask_question(
            "Choose site:",
            site_options,
            allow_random=False,
            default=site_options[0]
        )
        
        if choice['id'] == 'custom':
            custom_url = input("Enter custom URL: ").strip()
            return {
                'mode': 'custom',
                'url': custom_url,
                'enable_task_claim': True,
                'task_selectors': ["//button[contains(text(), 'Claim')]", "//*[contains(text(), 'Task')]"]
            }
        else:
            return {
                'mode': 'predefined',
                'site': 'gemek',
                **self.config['predefined_sites']['gemek']
            }
    
    def run_interactive_setup(self):
        """Run complete interactive setup"""
        print("🚀 Gemek Automation - Interactive Setup")
        print("=" * 50)
        
        self.scenario['accounts_count'] = self.get_accounts_count()
        self.scenario['headless_mode'] = self.get_headless_mode()
        self.scenario['device'] = self.get_device_scenario()
        self.scenario['location'] = self.get_location_scenario()
        self.scenario['stealth'] = self.get_stealth_scenario()
        self.scenario['proxy'] = self.get_proxy_scenario()
        self.scenario['task'] = self.get_task_scenario()
        self.scenario['site'] = self.get_site_choice()
        self.scenario['ip_auth'] = self.get_ip_auth_option()
        self.scenario['auth_mode'] = self.get_auth_mode()
        self.scenario['proxy_auth_method'] = self.get_proxy_auth_method()
        
        # Show summary
        self.show_scenario_summary()
        
        return self.scenario
    
    def show_scenario_summary(self):
        """Show the built scenario summary"""
        print("\n" + "=" * 50)
        print("📊 SCENARIO SUMMARY")
        print("=" * 50)
        print(f"📝 Accounts: {self.scenario['accounts_count']}")
        print(f"👁️  Headless: {'Yes' if self.scenario['headless_mode'] else 'No'}")
        print(f"📱 Device: {self.scenario['device']['name']}")
        print(f"🌍 Location: {self.scenario['location']['name']}")
        print(f"🕵️  Stealth: {self.scenario['stealth']['name'] if self.scenario['stealth'] else 'None'}")
        print(f"🔗 Proxy: {self.scenario['proxy']['name']}")
        print(f"🔐 IP Auth: {'Yes' if self.scenario['ip_auth'] else 'No'}")
        print(f"⌨️  Auth Mode: {'Auto-fill' if self.scenario['auth_mode'] == 'auto' else 'Manual input'}")
        print(f"🔐 Proxy Auth: {self.scenario['proxy_auth_method'].replace('_', ' ').title()}")
        print(f"🎯 Task: {self.scenario['task']['name']}")
        print(f"🌐 Site: {self.scenario['site']['url'] if self.scenario['site']['mode'] == 'custom' else self.scenario['site']['name']}")
        print("=" * 50)
        
        confirm = self.ask_yes_no("\nStart automation with this scenario?", default=True)
        return confirm

if __name__ == "__main__":
    runner = ScenarioRunner()
    scenario = runner.run_interactive_setup()
