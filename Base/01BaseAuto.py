from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
import time


class SettingsAutomation:
    """设置应用自动化类"""
    def __init__(self):
        self.driver = None
    def setup_driver(self, app_package, app_activity):
        """初始化驱动"""
        options = UiAutomator2Options()
        options.device_name = "PJZ110"
        options.platform_name = "Android"
        options.platform_version = "15"
        # options.app_package = "com.android.settings"
        # options.app_activity = ".Settings"
        options.app_package = app_package
        options.app_activity = app_activity
        options.no_reset = True

        self.driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', options=options)
        time.sleep(3)  # 等待应用加载
        return self.driver

    def quit_driver(self):
        """退出驱动"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def find_element(self, locator, by=AppiumBy.ID, timeout=10):
        """查找元素"""
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                element = self.driver.find_element(by, locator)
                if element.is_displayed():
                    return element
            except:
                time.sleep(0.5)
        raise Exception(f"元素未找到: {locator}")

    def click_element(self, locator, by=AppiumBy.ID):
        """点击元素"""
        element = self.find_element(locator, by)
        element.click()
        time.sleep(1)  # 等待操作完成

    def input_text(self, locator, text, by=AppiumBy.ID):
        """输入文本"""
        element = self.find_element(locator, by)
        element.clear()
        element.send_keys(text)

def main():
    auto = SettingsAutomation()
    damai_package = 'cn.damai'
    damai_activity = 'cn.damai.homepage.MainActivity'

    try:
        auto.setup_driver(damai_package,damai_activity)
        print("大麦APP启动成功！")
        # print(driver.page_source)
        auto.click_element(
            locator="//*[contains(@text,'我的')]",
            by=AppiumBy.XPATH
        )
        print("已点击我的")
        time.sleep(999)
    except Exception as e:
        print(f"运行出错: {str(e)}")
    finally:
        auto.quit_driver()

if __name__ == "__main__":
    main()