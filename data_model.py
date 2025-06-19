import pandas as pd
from io import StringIO
import re
import csv

class DataModel:
    def __init__(self):
        self.df = pd.DataFrame()

    def load_data_from_string(self, data_string: str, delimiter: str, header_row: int, skip_rows: int, quote_char: str):
        if not data_string.strip():
            self.df = pd.DataFrame()
            return True, "输入为空，预览已清空。"
        
        try:
            # Always define both quotechar and quoting to avoid pandas defaults ambiguity
            if quote_char is None:
                quoting = csv.QUOTE_NONE
                # Pass a dummy quotechar; it will be ignored by QUOTE_NONE
                effective_quote_char = '"' 
            else:
                quoting = csv.QUOTE_MINIMAL # Default pandas behavior
                effective_quote_char = quote_char

            self.df = pd.read_csv(
                StringIO(data_string),
                sep=delimiter,
                header=header_row,
                skiprows=skip_rows,
                quotechar=effective_quote_char,
                quoting=quoting,
                skipinitialspace=True,
                engine='python'
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

    def add_column(self, column_name: str):
        if not column_name:
            return "列名不能为空。"
        if column_name in self.df.columns:
            return f"列 '{column_name}' 已存在。"
        
        self.df[column_name] = None
        return f"已添加新列: {column_name}"

    def add_row(self):
        if self.df is not None:
            new_row_index = len(self.df)
            new_row = pd.DataFrame([['' for _ in self.df.columns]], columns=self.df.columns, index=[new_row_index])
            self.df = pd.concat([self.df, new_row])
            return new_row_index
        return None

    def update_cell(self, row_index, col_name, value):
        if self.df is not None:
            try:
                row_index = int(row_index)
                # Convert value to the column's dtype
                original_dtype = self.df[col_name].dtype
                if pd.api.types.is_numeric_dtype(original_dtype):
                    # Attempt to convert to numeric, but fall back to object if it fails
                    value = pd.to_numeric(value, errors='coerce')
                    if pd.isna(value):
                        # If conversion results in NaN (e.g., for non-numeric input)
                        # We might want to keep it as an object/string or handle as an error.
                        # For now, let's allow storing it as NaN if the column is numeric.
                        pass
                self.df.loc[row_index, col_name] = value
                # After modification, the data type may change, try to convert back
                self.df[col_name] = self.df[col_name].astype(original_dtype, errors='ignore')
            except (ValueError, TypeError) as e:
                print(f"Error updating cell: {e}")
                # Potentially revert or handle the error
                pass

    def get_data_for_display(self):
        """Ensures that the data returned to the view is always in a valid format."""
        if self.df is None:
            return ([], pd.DataFrame())
        return (self.df.columns, self.df)

    def export_to_excel(self, file_path: str):
        if self.df is None:
            return False, "没有可导出的数据。"
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