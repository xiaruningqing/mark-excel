import pandas as pd
from io import StringIO
import re

class DataModel:
    def __init__(self):
        self.df = pd.DataFrame()

    def load_data_from_string(self, data_string: str, delimiter: str, header_row: int, skip_rows: int, quote_char: str):
        if not data_string.strip():
            self.df = pd.DataFrame()
            return True, "输入为空，预览已清空。"
        
        try:
            self.df = pd.read_csv(
                StringIO(data_string),
                sep=delimiter,
                header=header_row,
                skiprows=skip_rows,
                quotechar=quote_char,
                skipinitialspace=True,
                engine='python' # Python engine is more robust for various delimiters
            )
            # After loading, remove columns that are all NaN (often artifacts of bad parsing)
            self.df.dropna(axis=1, how='all', inplace=True)
            return True, "数据加载成功。"
        except Exception as e:
            # On failure, keep the old dataframe instead of an empty one
            return False, f"数据解析失败: {e}"

    def clear_data(self):
        self.df = pd.DataFrame()

    def get_dataframe(self):
        return self.df

    def remove_empty_rows(self):
        initial_rows = len(self.df)
        self.df.dropna(how='all', inplace=True)
        rows_removed = initial_rows - len(self.df)
        return f"移除了 {rows_removed} 行空行。"

    def remove_duplicate_rows(self):
        initial_rows = len(self.df)
        self.df.drop_duplicates(inplace=True)
        rows_removed = initial_rows - len(self.df)
        return f"移除了 {rows_removed} 行重复行。"

    def normalize_column_names(self):
        def snake_case(s):
            return '_'.join(
                re.sub('([A-Z][a-z]+)', r' \1',
                re.sub('([A-Z]+)', r' \1',
                s.replace('-', ' '))).split()).lower()
        self.df.columns = [snake_case(col) for col in self.df.columns]
        return "已将所有列名规范化为蛇形命名法。"
        
    def fill_na_global(self, fill_value: str):
        self.df.fillna(fill_value, inplace=True)
        return f"已将所有空值填充为 '{fill_value}'。"

    def delete_rows_by_indices(self, indices: list[int]):
        initial_rows = len(self.df)
        self.df.drop(self.df.index[indices], inplace=True)
        self.df.reset_index(drop=True, inplace=True)
        rows_removed = initial_rows - len(self.df)
        return f"移除了 {rows_removed} 行。"

    def delete_columns_by_name(self, columns_to_delete: list):
        self.df.drop(columns=columns_to_delete, inplace=True)
        return f"已删除列: {', '.join(columns_to_delete)}"

    def update_cell(self, row_index: int, column_name: str, new_value: str):
        try:
            original_value = self.df.at[row_index, column_name]
            # Try to convert new_value to the original data type
            if new_value == "":
                 self.df.at[row_index, column_name] = None
            else:
                try:
                    # Attempt to cast to original type to maintain data integrity
                    dtype = self.df[column_name].dtype
                    converted_value = dtype.type(new_value)
                    self.df.at[row_index, column_name] = converted_value
                except (ValueError, TypeError):
                    # If casting fails, just assign the string
                    self.df.at[row_index, column_name] = new_value

            return f"单元格 ({row_index}, {column_name}) 的值已从 '{original_value}' 更新为 '{new_value}'"
        except Exception as e:
            return f"更新单元格失败: {e}"

    def export_to_excel(self, file_path: str):
        try:
            self.df.to_excel(file_path, index=False)
            return True, f"成功导出到 {file_path}"
        except Exception as e:
            return False, f"导出到 Excel 失败: {e}"

    def export_to_csv(self, file_path: str):
        try:
            self.df.to_csv(file_path, index=False, encoding='utf-8-sig')
            return True, f"成功导出到 {file_path}"
        except Exception as e:
            return False, f"导出到 CSV 失败: {e}" 