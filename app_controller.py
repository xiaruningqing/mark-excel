import customtkinter as ctk
from tkinter import filedialog
import os
import subprocess
import sys
import json
import logging
from datetime import datetime
from data_model import DataModel
from i18n import translator, get_translator
import chardet
from utils import detect_delimiter
import pandas as pd

EXAMPLE_DATA = """ID|Name|Age|City
1|Alice|30|New York
2|Bob|25|Los Angeles
2|Bob|25|Los Angeles
3|Charlie|35|Chicago
|David||
4|Eve|28|Houston
"""

class AppController:
    CONFIG_FILE = "config.json"

    def __init__(self, model: DataModel, view):
        self.model = model
        self.view = view
        self.view.set_controller(self)
        self._ = get_translator().get

    def _process_input_and_update_view(self, from_user_action=False):
        """
        Parses the input from the textbox and updates the table view.
        An internal method designed to avoid excessive logging during real-time updates.
        """
        input_text = self.view.textbox.get("1.0", "end-1c")
        message = None
        success = False
        
        if input_text.strip():
            try:
                delimiter = self.view.delimiter_var.get()
                if delimiter == '\\t': delimiter = '\t'
                header_row = int(self.view.header_row_var.get() or 0)
                skip_rows = int(self.view.skip_rows_var.get() or 0)
                quote_char_val = self.view.quote_char_var.get()
                quote_char = None if quote_char_val == self._("no_quote_char") else quote_char_val
                
                success, message = self.model.load_data_from_string(input_text, delimiter, header_row, skip_rows, quote_char)
                
                if success and from_user_action:
                    self.log_and_update_status(message)
                
                if not success:
                    self.model.clear_data()
                    if from_user_action:
                        self.log_and_update_status(self._("status_error_parsing").format(error=message), level="error")

            except (ValueError, TypeError) as e:
                 if from_user_action:
                    self.log_and_update_status(self._("log_error_invalid_settings"), level="error")
                 self.model.clear_data()
        else:
            self.model.clear_data()
            if from_user_action:
                 self.log_and_update_status(self._("status_ready"))

        self.view.update_table(*self.model.get_data_for_display())
        
        if success and from_user_action:
            detected_delimiter = detect_delimiter(input_text)
            if detected_delimiter:
                ui_delimiter = '\\t' if detected_delimiter == '\t' else detected_delimiter
                if self.view.delimiter_var.get() != ui_delimiter:
                    self.view.delimiter_var.set(ui_delimiter)

    def process_input_data(self):
        """Public method for the debounce timer, which should not log."""
        self._process_input_and_update_view(from_user_action=False)

    def log_and_update_status(self, message: str, level: str = "info"):
        if level == "info": logging.info(message)
        else: logging.error(message)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.view.add_history(f"[{timestamp}] {message}")
        self.view.update_status(message)

    def _run_data_op(self, operation, *args):
        if self.model.df is None or self.model.df.empty:
            self.log_and_update_status(self._("log_error_no_data_op"), level="error")
            return
        message = operation(*args)
        self.view.update_table(*self.model.get_data_for_display())
        self.log_and_update_status(message)

    def on_remove_empty_rows(self): self._run_data_op(self.model.remove_empty_rows)
    def on_remove_duplicate_rows(self): self._run_data_op(self.model.remove_duplicate_rows)
    def on_normalize_column_names(self): self._run_data_op(self.model.normalize_column_names)

    def on_fill_na_global(self):
        fill_value = self.view.fill_na_entry.get()
        if not fill_value:
            self.log_and_update_status(self._("log_error_no_fill_value"), level="error")
            return
        self._run_data_op(self.model.fill_na_global, fill_value)

    def on_delete_selected_rows(self):
        selected_items = self.view.tree.selection()
        if not selected_items:
            self.log_and_update_status(self._("log_error_no_rows_selected"), level="error")
            return
        indices_to_delete = [self.view.tree.index(item) for item in selected_items]
        self._run_data_op(self.model.delete_rows_by_indices, indices_to_delete)

    def on_manage_columns(self):
        if self.model.df is None:
            return

        toplevel = ctk.CTkToplevel(self.view)
        toplevel.title(self._("manage_columns_title"))
        toplevel.geometry("400x550")
        toplevel.transient(self.view)

        ctk.CTkLabel(toplevel, text=self._("manage_columns_prompt_delete"), font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(10, 5))
        
        scrollable_frame = ctk.CTkScrollableFrame(toplevel, height=300)
        scrollable_frame.pack(fill="x", expand=True, padx=10)
        column_vars = {name: ctk.BooleanVar(value=True) for name in self.model.df.columns}
        for name, var in column_vars.items():
            ctk.CTkCheckBox(scrollable_frame, text=name, variable=var).pack(anchor="w", padx=10, pady=5)

        ctk.CTkLabel(toplevel, text=self._("manage_columns_prompt_add"), font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(20, 5))
        
        add_frame = ctk.CTkFrame(toplevel)
        add_frame.pack(pady=5, padx=10, fill="x")
        new_col_entry = ctk.CTkEntry(add_frame, placeholder_text=self._("add_column_placeholder"))
        new_col_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        def apply_and_close():
            cols_to_delete = [name for name, var in column_vars.items() if not var.get()]
            if cols_to_delete:
                self._run_data_op(self.model.delete_columns_by_name, cols_to_delete)
            
            new_col_name = new_col_entry.get()
            if new_col_name:
                self._run_data_op(self.model.add_column, new_col_name)

            toplevel.destroy()

        add_button = ctk.CTkButton(add_frame, text=self._("add_button"), width=80, command=lambda: self._run_data_op(self.model.add_column, new_col_entry.get()))
        
        button_frame = ctk.CTkFrame(toplevel, fg_color="transparent")
        button_frame.pack(pady=(20,10), fill="x", side="bottom")

        apply_button = ctk.CTkButton(button_frame, text=self._("apply_and_close_button"), command=apply_and_close)
        apply_button.pack(side="right", padx=10)
        
        cancel_button = ctk.CTkButton(button_frame, text=self._("cancel_button"), command=toplevel.destroy)
        cancel_button.pack(side="right", padx=10)

    def on_cell_update(self, row_index, column_name, new_value):
        self.model.update_cell(row_index, column_name, new_value)
        update_message = self._("history_cell_updated").format(row=row_index + 1, col=column_name, val=new_value)
        self.log_and_update_status(update_message)

    def run(self):
        self.load_config()
        self.view.mainloop()

    def on_add_row(self):
        if self.model.df is None:
            self.log_and_update_status(self._("log_error_no_data_for_add_row"), level="error")
            return
            
        new_row_index = self.model.add_row()
        if new_row_index is not None:
            self.view.update_table(*self.model.get_data_for_display())
            self.view.add_history(self._("history_row_added"))
            # Focus on the first cell of the new row
            self.view.focus_and_edit_cell(new_row_index, 0)

    def on_file_drop(self, file_path_str: str):
        file_path = file_path_str.strip('{}')
        allowed_extensions = ['.txt', '.csv', '.tsv', '.md']
        if not any(file_path.lower().endswith(ext) for ext in allowed_extensions):
            self.log_and_update_status(self._("log_warning_unsupported_format").format(file=os.path.basename(file_path)), level="info")
        content, used_encoding = self.read_file_robustly(file_path)
        if content is not None:
            self.view.textbox.delete("1.0", "end")
            self.view.textbox.insert("1.0", content)
            self._process_input_and_update_view(from_user_action=True)
        else:
            self.log_and_update_status(self._("log_error_file_decode_failed").format(file=os.path.basename(file_path)), level="error")
    
    def read_file_robustly(self, file_path):
        encodings_to_try = ['utf-8']
        try:
            with open(file_path, 'rb') as f_raw:
                detected = chardet.detect(f_raw.read(1024*20))
                if detected['encoding']: encodings_to_try.insert(0, detected['encoding'])
        except Exception: pass
        encodings_to_try.extend(['gbk', 'latin1', 'utf-16'])
        for encoding in list(dict.fromkeys(encodings_to_try)):
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    self.log_and_update_status(self._("log_info_file_loaded").format(file=os.path.basename(file_path), encoding=encoding))
                    return f.read(), encoding
            except (UnicodeDecodeError, TypeError): continue
            except Exception as e:
                # logging.error(f"Error reading file {file_path} with {encoding}: {e}")
                return None, None
        return None, None

    def on_load_example_data(self):
        self.view.textbox.delete("1.0", "end")
        self.view.textbox.insert("1.0", EXAMPLE_DATA)
        self._process_input_and_update_view(from_user_action=True)
        
    def _export_file(self, file_type: str):
        if self.model.df.empty:
            self.log_and_update_status(self._("log_error_no_data_export"), level="error"); return
        file_path, export_func = (filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")]), self.model.export_to_excel) if file_type == 'excel' else (filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")]), self.model.export_to_csv)
        if not file_path:
            self.log_and_update_status(self._("log_info_export_cancelled")); return
        success, message = export_func(file_path)
        self.log_and_update_status(message)
        if success and self.view.open_after_export_var.get():
            try:
                if sys.platform == "win32": os.startfile(file_path)
                elif sys.platform == "darwin": subprocess.call(["open", file_path])
                else: subprocess.call(["xdg-open", file_path])
            except Exception as e:
                self.log_and_update_status(self._("log_error_auto_open_failed").format(e=e), level="error")

    def on_export_to_excel(self): self._export_file('excel')
    def on_export_to_csv(self): self._export_file('csv')

    def on_switch_language(self, lang_choice: str):
        lang_code = "zh" if lang_choice == "中文" else "en"
        translator.set_language(lang_code)
        self._ = get_translator().get
        self.view.update_ui_text()
        self.log_and_update_status(self._("log_info_lang_switched").format(lang=lang_choice))

    def save_config(self):
        try:
            config = self.view.get_settings()
            config["language"] = translator.language
            with open(self.CONFIG_FILE, 'w') as f: json.dump(config, f, indent=4)
            logging.info("Configuration saved.")
        except Exception as e:
            logging.error(f"Failed to save config: {e}")

    def load_config(self):
        config = {}
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                self.log_and_update_status(self._("log_info_config_loaded"))
            except Exception as e:
                self.log_and_update_status(self._("log_error_config_load_failed").format(e=e), level="error")

        lang = config.get("language", "zh")
        translator.set_language(lang)
        self._ = get_translator().get
        
        self.view.update_ui_text()
        self.view.set_settings(config) 