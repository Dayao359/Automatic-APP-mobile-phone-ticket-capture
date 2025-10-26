from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
import time
import subprocess


class SettingsAutomation:
    """设置应用自动化类"""

    def __init__(self):
        self.driver = None

    def cleanup_uiautomator2(self):
        """清理UiAutomator2相关应用"""
        print("清理UiAutomator2残留...")
        try:
            # 强制停止并卸载UiAutomator2相关包
            packages = [
                "io.appium.uiautomator2.server",
                "io.appium.uiautomator2.server.test",
                "io.appium.settings"
            ]

            for package in packages:
                subprocess.run(
                    ['adb', 'shell', 'pm', 'uninstall', package],
                    capture_output=True,
                    timeout=10
                )
                print(f"已清理: {package}")

            # 清理缓存
            subprocess.run(['adb', 'shell', 'pm', 'clear', 'io.appium.settings'], timeout=10)
            time.sleep(2)

        except Exception as e:
            print(f"清理过程中出现警告: {e}")

    def setup_driver(self, app_package, app_activity):
        """初始化驱动"""
        # 先清理残留
        # self.cleanup_uiautomator2()
        # 创建初始化Android设备配置选项
        options = UiAutomator2Options()
        # 设备基础信息配置
        options.device_name = "PJZ110"  # 设备名称
        options.platform_name = "Android"  # 平台类型
        options.platform_version = "15"  # 设备Android系统版本
        options.app_package = app_package  # 目标APP的包名
        options.app_activity = app_activity  # 目标APP的启动页Activity

        # 启动行为配置
        options.no_reset = True  # 启动时不重置APP数据
        options.skip_unlock = True  # 跳过设备解锁
        options.unicode_keyboard = True  # 启用Unicode键盘

        # 针对Android 15的兼容性设置
        options.uiautomator2_server_launch_timeout = 45000  # UIAutomator2服务启动超时
        options.uiautomator2_server_install_timeout = 60000  # UIAutomator2服务安装超时
        options.android_install_timeout = 60000  # APP安装
        options.adb_exec_timeout = 40000  # ADB命令执行超时

        # 禁用可能导致崩溃的功能
        options.disable_window_animation = True  # Android 15可能需要启用动画
        options.auto_grant_permissions = True  # 自动授予APP所需权限
        options.enable_notifications = False  # 禁用通知监听

        # 强制重新安装服务器
        options.force_app_launch = True  # 强制启动APP
        options.enable_webview_details_collection = False  # 禁用WebView详情收集

        print("正在启动Appium驱动...")
        start_time = time.time()
        self.driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', options=options)
        setup_time = time.time() - start_time
        print(f"驱动启动成功！耗时: {setup_time:.2f}秒")
        return self.driver

    def quit_driver(self):
        """退出驱动"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            print("驱动已退出")

    def wait_for_element(self, locator, by=AppiumBy.ID, max_retry=3):
        """智能等待元素出现"""
        retry_count = 0  # 重试次数计数器，初始为0

        while retry_count < max_retry:
            try:
                # 尝试查找元素，并判断是否可见且可交互
                element = self.driver.find_element(by, locator)
                if element.is_displayed() and element.is_enabled():
                    return element
            # 只捕获“元素没找到”或“元素不可见”的异常，不吞其他错误
            except:
                retry_count += 1  # 重试次数+1
                # 判断是否已达到最大重试次数
                if retry_count >= max_retry:
                    raise Exception(f"找不到元素：{locator}（已重试{max_retry}次）")

        # 理论上不会走到这里，保险起见仍抛出异常
        raise Exception(f"找不到元素：{locator}（已重试{max_retry}次）")

    def click_element(self, locator, by=AppiumBy.ID, timeout=20):
        """点击元素"""
        element = self.wait_for_element(locator, by, timeout)
        click_start = time.time()
        element.click()
        click_time = time.time() - click_start
        print(f"点击完成，耗时: {click_time:.2f}秒")
        time.sleep(1.5)


def main():
    auto = SettingsAutomation()
    damai_package = 'cn.damai'
    damai_activity = 'cn.damai.homepage.MainActivity'

    try:
        # 启动驱动
        auto.setup_driver(damai_package, damai_activity)
        print("大麦APP启动成功！")

        # 点击"我的"标签
        auto.click_element(
            locator="//android.widget.TextView[@resource-id='cn.damai:id/bottom_tab_item_tv' and @text='我的']",
            by=AppiumBy.XPATH
        )
        # 点击"想看"标签
        auto.click_element(
            locator="//android.widget.TextView[@text='想看']",
            by=AppiumBy.XPATH
        )
        # 点击"购票"标签
        auto.click_element(
            locator="//android.widget.TextView[@text='购票']",
            by=AppiumBy.XPATH
        )
        # 点击"已预约"标签
        auto.click_element(
            locator="cn.damai:id/trade_project_detail_purchase_status_bar_container_fl",
            by=AppiumBy.ID
        )
        # 验证点击结果
        print("操作完成！")

    except Exception as e:
        print(f"运行出错: {str(e)}")
    finally:
        auto.quit_driver()


if __name__ == "__main__":
    main()
