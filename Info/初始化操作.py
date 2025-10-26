from appium import webdriver
from appium.options.android import UiAutomator2Options
import time

options = UiAutomator2Options()
options.device_name = "PJZ110"
options.platform_name = "Android"
options.platform_version = "15"
options.app_package = "com.android.settings"
options.app_activity = ".Settings"  # 改为主页面的Activity
options.no_reset = True

driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', options=options)
time.sleep(5)
driver.quit()