from datetime import datetime, timedelta
import pymysql as ps
import pandas as pd
import numpy as np
import zipfile
import random
import time
import os
import zipfile
import re


# Base.py
class Base():
    def __init__(self, uploada_dir=None):
        self.connection = None
        self.cursor = None
        if uploada_dir:
            self.uploada_dir = uploada_dir

    # *******************************************路径操作************************************************
    def get_files_from_dir(self, directory):
        """获取指定路径下所有文件路径"""
        files = []
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                files.append(os.path.join(root, filename))
        return files

    def read_path_concat(self, directory):
        """将文件夹下所有excel合并"""
        all_dfs = []
        # 检查路径是否为有效目录
        if not os.path.isdir(directory):
            print(f"警告：{directory} 不是有效的目录路径")
            return pd.DataFrame()  # 返回空DataFrame

        for excel_file in os.listdir(directory):
            if excel_file.endswith(('.xlsx', '.xls')):
                data_path = os.path.join(directory, excel_file)
                try:
                    df = pd.read_excel(data_path, sheet_name=0)
                    all_dfs.append(df)
                except Exception as e:
                    print(f"读取文件 {excel_file} 失败：{e}")
                    continue

        if all_dfs:
            merged_df = pd.concat(all_dfs, ignore_index=True)
            return merged_df
        else:
            return pd.DataFrame()

    def drop_path_file(self, path):
        """删除路径下所有文件"""
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            os.remove(item_path)

    def cleanup_downloaded_files(self, file_paths):
        """清理下载的Excel文件"""
        if not file_paths:
            return
        deleted_count = 0
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_count += 1
            except Exception as e:
                print(f"删除文件失败 {file_path}: {e}")

    def get_files_from_dirs(self, dir_sale, Name):
        """获取指定路径下指定文件名下的文件做处理,特用于处理csv文件"""
        sale_dfs = []
        for file_path in dir_sale:
            if Name in file_path:
                try:
                    # 处理csv文件
                    if file_path.endswith(".csv"):
                        try:
                            df = pd.read_csv(file_path, encoding='gbk')
                        except UnicodeDecodeError:
                            df = pd.read_csv(file_path, encoding='utf-8')
                        sale_dfs.append(df)
                        # 处理Excel文件
                    elif file_path.endswith(".xlsx") or file_path.endswith(".xls"):
                        df = pd.read_excel(file_path)
                        sale_dfs.append(df)
                except Exception as e:
                    # 捕获所有读取异常，避免单个文件错误中断整个流程
                    print(f"读取文件失败 {file_path}：{str(e)}")
                    continue
        if sale_dfs:
            combined_df = pd.concat(sale_dfs, ignore_index=True)
            return combined_df
        else:
            print(f"未找到含'{Name}'的CSV或Excel文件")
            return None

    # *******************************************解压操作************************************************
    def extract_all_zip_files(self, directory_path):
        """
        解压目录中的所有zip文件并删除原压缩包
        Args:directory_path: 包含压缩包的目录路径
        Returns:list: 解压后的文件路径列表
        """
        extracted_files = []
        # 确保目录存在
        if not os.path.exists(directory_path):
            print(f"目录不存在: {directory_path}")
            return extracted_files
        # 获取目录中的所有文件
        all_files = os.listdir(directory_path)
        zip_files = [f for f in all_files if f.endswith(('.zip', '.rar', '.7z'))]
        if not zip_files:
            print("未找到压缩包文件")
            return extracted_files
        print(f"找到 {len(zip_files)} 个压缩包文件")
        for zip_file in zip_files:
            zip_path = os.path.join(directory_path, zip_file)

            try:
                # 解压zip文件
                if zip_file.endswith('.zip'):
                    extracted = self.extract_zip_file(zip_path, directory_path)
                    extracted_files.extend(extracted)
                    # 删除原压缩包
                    os.remove(zip_path)
                # 可以添加其他格式的支持，如rar、7z等
                # elif zip_file.endswith('.rar'):
                #     extract_rar_file(zip_path, directory_path)

            except Exception as e:
                print(f"解压文件 {zip_file} 失败: {e}")
                continue
        return extracted_files

    def extract_zip_file(self, zip_path, extract_to):
        """
        解压单个zip文件
        Args:
            zip_path: zip文件路径
            extract_to: 解压目标目录
        Returns:
            list: 解压出的文件路径列表
        """
        extracted_files = []
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # 获取zip文件中的所有文件列表
                file_list = zip_ref.namelist()
                # 解压所有文件
                zip_ref.extractall(extract_to)
                # 记录解压出的文件
                for file_name in file_list:
                    extracted_path = os.path.join(extract_to, file_name)
                    if os.path.isfile(extracted_path):  # 只记录文件，不记录目录
                        extracted_files.append(extracted_path)
        except zipfile.BadZipFile:
            print(f"文件损坏或不是有效的zip文件: {zip_path}")
        except Exception as e:
            print(f"解压过程中发生错误: {e}")
        return extracted_files

    # *******************************************PANDAS操作************************************************
    def clean_columns_and_values(self, df, numeric_cols=None):
        """
        清洗DataFrame的列名和值
        Args:
            df: 要清洗的DataFrame
            numeric_cols: 需要转换为数值类型的列名列表
        Returns:
            清洗后的DataFrame
        """
        if df is None or df.empty:
            return df
        # 创建副本以避免修改原始数据
        df_cleaned = df.copy()
        try:
            # 1. 清洗列名（去除制表符和空白）
            df_cleaned.columns = [str(col).replace('\t', '').strip() for col in df_cleaned.columns]
            # 2. 清洗每列的值
            for col in df_cleaned.columns:
                if col in df_cleaned.columns:  # 确保列仍然存在
                    # 将列值转换为字符串并清洗
                    series_cleaned = df_cleaned[col].astype(str)
                    series_cleaned = series_cleaned.str.replace('\t', '', regex=False)
                    series_cleaned = series_cleaned.str.strip()
                    # 将空字符串转为NaN
                    series_cleaned = series_cleaned.replace('', pd.NA)
                    series_cleaned = series_cleaned.replace('nan', pd.NA)
                    series_cleaned = series_cleaned.replace('None', pd.NA)
                    # 如果是需要保留数值的列，尝试转回数值类型
                    if numeric_cols and col in numeric_cols:
                        try:
                            # 先尝试直接转换
                            numeric_series = pd.to_numeric(series_cleaned, errors='coerce')
                            df_cleaned[col] = numeric_series
                        except Exception as e:
                            print(f"列 {col} 转换为数值失败: {e}")
                            df_cleaned[col] = series_cleaned
                    else:
                        df_cleaned[col] = series_cleaned
            return df_cleaned
        except Exception as e:
            print(f"清洗数据时发生错误: {e}")
            return df

    # *******************************************XPATH操作************************************************
    def click_by_xpath(self, web, xpath, timeout=10, element_index=0):
        """
        通过XPath查找元素并点击（内置JS点击逻辑）
        :param web: 浏览器实例
        :param xpath: 元素XPath表达式
        :param timeout: 查找元素超时时间（秒）
        :param element_index: 多元素时选择的索引（默认第1个）
        :return: bool - 点击是否成功
        """
        try:
            # 1. 查找元素
            elements = web.find_all_by_xpath(xpath, timeout=timeout)
            if not elements:
                print(f"未找到匹配XPath的元素: {xpath}")
                return False
            # 2. 验证索引有效性
            if element_index < 0 or element_index >= len(elements):
                print(f"元素索引{element_index}无效（共{len(elements)}个元素）")
                return False
            target_element = elements[element_index]
            # 3. 定义JS点击函数
            js_script = """
            function(element) {
                try {
                    element.click();
                    return "click_success";
                } catch (error) {
                    return "click_error: " + error.message;
                }
            }
            """
            # 4. 执行JS点击
            try:
                result = target_element.execute_javascript(js_script)
                if result == "click_success":
                    return True
                else:
                    print(f"JS点击失败: {result}")
                    return False
            except Exception as js_err:
                print(f"JS执行异常: {str(js_err)}")
                return False
        except Exception as e:
            print(f"点击流程异常: {str(e)}")
            return False

    def get_text_by_xpath(self, web, xpath, element_index=0, default_text=""):
        """获取XPath获取元素文本"""
        try:
            # 查找所有匹配的元素
            elements = web.find_all_by_xpath(xpath, timeout=10)
            if not elements:
                print(f"未找到匹配XPath的元素: {xpath}")
                return default_text
            if element_index >= len(elements):
                print(f"元素索引 {element_index} 超出范围，总共找到 {len(elements)} 个元素")
                return default_text
            # 获取指定元素的文本
            element = elements[element_index]
            text = element.get_text()
            # 清理文本（去除首尾空格和换行符）
            cleaned_text = text.strip() if text else default_text
            return cleaned_text
        except Exception as e:
            print(f"获取文本失败: {e} (XPath: {xpath})")
            return default_text

    # *******************************************时间操作************************************************
    def get_yesterday_date(self, days=1):
        """获取前一天的日期"""
        today = datetime.now()
        yesterday = today - timedelta(days)
        return yesterday.strftime('%Y-%m-%d')

    def sleep_time(self, start_time=1, end_time=2):
        """随机时长休息"""
        sleep_time = random.uniform(start_time, end_time)
        return time.sleep(sleep_time)

    # *******************************************下载操作************************************************
    def download_file(self, webBrowser, xpath, n=0):
        """
        文件下载
        * @param webBrowser,打开的网页对象
        * @param xpath,页面下载按钮的xpath路径
        * @param n,页面下载按钮元素序列，定位到多个时默认第一个
        * @return file_path,返回下载后文件路径

        """
        base_path = os.getcwd()
        tmp_path = os.path.join(base_path, "tmp_file_path")
        os.makedirs(tmp_path, exist_ok=True)

        download_btn = webBrowser.find_all_by_xpath(xpath, timeout=3)[n]
        webBrowser.wait_load_completed(300)
        if download_btn.is_enabled():
            download_btn.click(simulative=False)
            file_path = xbot.web.handle_save_dialog(tmp_path, "ok", wait_complete=True, mode="chrome",
                                                    wait_complete_timeout=6 * 60, simulative=True)
            return file_path
        else:
            xbot.logging.info("下载按钮无法使用，查看是否无数据或其他原因")
            return None

