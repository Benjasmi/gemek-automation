# Device Pool Package
from .android_pool import ANDROID_DEVICES
from .iphone_pool import IPHONE_DEVICES
from .desktop_pool import DESKTOP_DEVICES
from .device_manager import DeviceManager

__all__ = ['ANDROID_DEVICES', 'IPHONE_DEVICES', 'DESKTOP_DEVICES', 'DeviceManager']
