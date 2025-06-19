import json
import os
from utils import resource_path

class Translator:
    def __init__(self):
        self.language_data = {}
        self.language = "zh"
        
        # Determine path to translations folder
        self.translations_path = resource_path('i18n')
        if not os.path.exists(self.translations_path):
            os.makedirs(self.translations_path)
            self._create_default_translations()
            
        self._load_language_data()

    def _create_default_translations(self):
        zh_translations = {
            "app_title": "Mark Excel - 表格数据整理工具",
            "status_ready": "就绪",
            "input_data_label": "输入数据",
            "hint_text": "在此粘贴数据 (Markdown, CSV, TSV) 或拖入文件",
            "example_data_button": "示例数据",
            "settings_label": "解析与清理设置",
            "delimiter_label": "分隔符:",
            "custom_delimiter_label": "自定义:",
            "header_row_label": "表头行:",
            "skip_rows_label": "跳过行:",
            "quote_char_label": "引号字符:",
            "no_quote_char": "无",
            "cleaning_label": "数据清理",
            "remove_empty_rows_button": "移除空行",
            "remove_duplicates_button": "移除重复行",
            "normalize_columns_button": "规范化列名",
            "fill_na_placeholder": "输入用于填充空值的内容",
            "fill_na_button": "填充空值",
            "export_label": "导出",
            "export_excel_button": "导出为 Excel (.xlsx)",
            "export_csv_button": "导出为 CSV (.csv)",
            "open_after_export_check": "导出后自动打开文件",
            "preview_label": "实时预览",
            "manage_columns_button": "管理列...",
            "delete_rows_button": "删除选中行",
            "manage_columns_title": "管理列",
            "manage_columns_prompt": "取消勾选以删除列:",
            "cancel_button": "取消",
            "apply_button": "应用",
            "log_info_app_start": "应用启动",
            "log_info_file_loaded": "已加载文件: {file} (编码: {encoding})",
            "log_warning_unsupported_format": "警告: 文件 {file} 可能不是支持的文本格式。",
            "log_error_file_decode_failed": "错误: 无法解码文件 {file}。请确保它是UTF-8, GBK等编码的文本文件。",
            "log_error_no_data_op": "操作失败：没有可操作的数据。",
            "log_error_no_fill_value": "操作失败：未提供用于填充的值。",
            "log_error_no_rows_selected": "操作失败：未选择任何行。",
            "log_error_no_cols_manage": "操作失败：没有可管理的列。",
            "log_error_no_data_export": "导出失败：没有可导出的数据。",
            "log_info_export_cancelled": "导出操作已取消。",
            "log_error_auto_open_failed": "自动打开文件失败: {e}",
            "log_info_lang_switched": "语言已切换至: {lang}",
            "log_info_config_loaded": "配置已加载。",
            "status_preview": "预览: {rows} 行, {cols} 列",
            "log_error_config_load_failed": "加载配置失败: {e}",
            "log_error_invalid_settings": "设置值无效(例如，行号必须是数字)。",
            "tooltip_remove_empty": "删除所有值均为空的行。",
            "tooltip_remove_duplicates": "删除内容完全相同的重复行。",
            "tooltip_normalize_columns": "将列名转换为小写下划线蛇形命名法 (e.g. 'Column Name' -> 'column_name')",
            "tooltip_fill_na": "使用左侧输入框中的文本替换所有单元格的空值。"
        }
        
        en_translations = {
            "app_title": "Mark Excel - Data Cleaning Tool",
            "status_ready": "Ready",
            "input_data_label": "Input Data",
            "hint_text": "Paste data here (Markdown, CSV, TSV) or drop a file",
            "example_data_button": "Example Data",
            "settings_label": "Parsing & Cleaning Settings",
            "delimiter_label": "Delimiter:",
            "custom_delimiter_label": "Custom:",
            "header_row_label": "Header row:",
            "skip_rows_label": "Skip rows:",
            "quote_char_label": "Quote Char:",
            "no_quote_char": "None",
            "cleaning_label": "Data Cleaning",
            "remove_empty_rows_button": "Remove Empty Rows",
            "remove_duplicates_button": "Remove Duplicates",
            "normalize_columns_button": "Normalize Columns",
            "fill_na_placeholder": "Enter value to fill empty cells",
            "fill_na_button": "Fill NA",
            "export_label": "Export",
            "export_excel_button": "Export to Excel (.xlsx)",
            "export_csv_button": "Export to CSV (.csv)",
            "open_after_export_check": "Open file after export",
            "preview_label": "Live Preview",
            "manage_columns_button": "Manage Columns...",
            "delete_rows_button": "Delete Selected Rows",
            "manage_columns_title": "Manage Columns",
            "manage_columns_prompt": "Uncheck columns to delete:",
            "cancel_button": "Cancel",
            "apply_button": "Apply",
            "log_info_app_start": "Application started",
            "log_info_file_loaded": "File loaded: {file} (encoding: {encoding})",
            "log_warning_unsupported_format": "Warning: File {file} may not be a supported text format.",
            "log_error_file_decode_failed": "Error: Could not decode file {file}. Please ensure it's a text file with UTF-8, GBK, etc. encoding.",
            "log_error_no_data_op": "Operation failed: No data to operate on.",
            "log_error_no_fill_value": "Operation failed: No fill value provided.",
            "log_error_no_rows_selected": "Operation failed: No rows selected.",
            "log_error_no_cols_manage": "Operation failed: No columns to manage.",
            "log_error_no_data_export": "Export failed: No data to export.",
            "log_info_export_cancelled": "Export operation cancelled.",
            "log_error_auto_open_failed": "Failed to auto-open file: {e}",
            "log_info_lang_switched": "Language switched to: {lang}",
            "log_info_config_loaded": "Configuration loaded.",
            "status_preview": "Preview: {rows} rows, {cols} columns",
            "log_error_config_load_failed": "Failed to load config: {e}",
            "log_error_invalid_settings": "Invalid setting value (e.g., row numbers must be integers).",
            "tooltip_remove_empty": "Delete rows where all values are empty.",
            "tooltip_remove_duplicates": "Delete rows that are exact duplicates of another row.",
            "tooltip_normalize_columns": "Convert column names to lowercase snake_case (e.g. 'Column Name' -> 'column_name')",
            "tooltip_fill_na": "Replace all empty cells with the text from the input box on the left."
        }
        
        with open(os.path.join(self.translations_path, 'zh.json'), 'w', encoding='utf-8') as f:
            json.dump(zh_translations, f, ensure_ascii=False, indent=4)
        with open(os.path.join(self.translations_path, 'en.json'), 'w', encoding='utf-8') as f:
            json.dump(en_translations, f, ensure_ascii=False, indent=4)

    def _load_language_data(self):
        for lang_code in ["zh", "en"]:
            try:
                with open(os.path.join(self.translations_path, f'{lang_code}.json'), 'r', encoding='utf-8') as f:
                    self.language_data[lang_code] = json.load(f)
            except FileNotFoundError:
                # If a file is missing, it will be created with defaults
                self._create_default_translations()
                with open(os.path.join(self.translations_path, f'{lang_code}.json'), 'r', encoding='utf-8') as f:
                    self.language_data[lang_code] = json.load(f)

    def set_language(self, language_code):
        if language_code in self.language_data:
            self.language = language_code
        else:
            # Fallback to English if the language is not supported
            self.language = "en"

    def get(self, key):
        return self.language_data.get(self.language, {}).get(key, key)

translator = Translator()

def get_translator():
    return translator