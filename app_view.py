import customtkinter as ctk
from tkinter import ttk
from PIL import Image
import os
from tkinterdnd2 import DND_FILES
from i18n import get_translator
from utils import Tooltip
import logging

class AppView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.controller = None
        self._debounce_timer = None
        self._edit_entry = None # Track the current edit entry
        self.pack(fill="both", expand=True)

        self.style = ttk.Style()
        self.icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")
        self.input_icon = self._load_icon("input.png")
        self.settings_icon = self._load_icon("settings.png")
        self.preview_icon = self._load_icon("preview.png")

        self._create_widgets()
        self.update_ui_text() 
        self.update_treeview_style()
        
    def set_controller(self, controller):
        self.controller = controller
        
        self.textbox.bind("<KeyRelease>", self._debounce_input, add="+")
        self.textbox.drop_target_register(DND_FILES)
        self.textbox.dnd_bind('<<Drop>>', lambda e: self.controller.on_file_drop(e.data))
        
        self.example_data_button.configure(command=self.controller.on_load_example_data)
        self.lang_switch.configure(command=self.controller.on_switch_language)
        self.remove_empty_button.configure(command=self.controller.on_remove_empty_rows)
        self.remove_duplicates_button.configure(command=self.controller.on_remove_duplicate_rows)
        self.normalize_columns_button.configure(command=self.controller.on_normalize_column_names)
        self.fill_na_button.configure(command=self.controller.on_fill_na_global)
        self.export_excel_button.configure(command=self.controller.on_export_to_excel)
        self.export_csv_button.configure(command=self.controller.on_export_to_csv)
        self.delete_rows_button.configure(command=self.controller.on_delete_selected_rows)
        self.manage_columns_button.configure(command=self.controller.on_manage_columns)

        self.tree.bind("<Double-1>", self.on_treeview_double_click)

        self.delimiter_var.trace_add("write", self._debounce_input)
        self.header_row_var.trace_add("write", self._debounce_input)
        self.skip_rows_var.trace_add("write", self._debounce_input)
        self.quote_char_var.trace_add("write", self._debounce_input)

    def _create_widgets(self):
        _ = get_translator().get
        self.grid_columnconfigure(0, weight=1, minsize=350); self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1); self.grid_rowconfigure(1, weight=0)
        
        self.left_frame = ctk.CTkFrame(self, width=400, corner_radius=0); self.left_frame.grid(row=0, column=0, sticky="nsew")
        self.left_frame.grid_rowconfigure(0, weight=1); self.left_frame.grid_rowconfigure(1, weight=1)
        self.right_frame = ctk.CTkFrame(self); self.right_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.right_frame.grid_columnconfigure(0, weight=1); self.right_frame.grid_rowconfigure(0, weight=1); self.right_frame.grid_rowconfigure(1, weight=0)

        bottom_frame = ctk.CTkFrame(self); bottom_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        bottom_frame.grid_columnconfigure(0, weight=1)
        self.history_log = ctk.CTkTextbox(bottom_frame, height=100); self.history_log.pack(fill="x", expand=True, padx=5, pady=(5,0)); self.history_log.configure(state="disabled")
        self.status_bar = ctk.CTkFrame(bottom_frame, height=30); self.status_bar.pack(fill="x", expand=True, padx=5, pady=(0,5))
        self.status_label = ctk.CTkLabel(self.status_bar, text=""); self.status_label.pack(side="left", padx=10)

        self.input_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent"); self.input_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.input_frame.grid_columnconfigure(0, weight=1); self.input_frame.grid_rowconfigure(2, weight=1)
        input_header_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent"); input_header_frame.grid(row=0, column=0, sticky="ew")
        input_header_frame.grid_columnconfigure(0, weight=1)
        self.input_label = ctk.CTkLabel(input_header_frame, image=self.input_icon, compound="left", font=ctk.CTkFont(size=15, weight="bold")); self.input_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.hint_label = ctk.CTkLabel(self.input_frame, text_color="gray", font=ctk.CTkFont(size=12)); self.hint_label.grid(row=1, column=0, sticky="w", padx=5, pady=(0,5))
        self.example_data_button = ctk.CTkButton(input_header_frame, width=80); self.example_data_button.grid(row=0, column=1, sticky="e", padx=5, pady=5)
        self.textbox = ctk.CTkTextbox(self.input_frame); self.textbox.grid(row=2, column=0, columnspan=2, sticky="nsew")

        self.settings_frame = ctk.CTkScrollableFrame(self.left_frame, fg_color="transparent"); self.settings_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10); self.settings_frame.grid_columnconfigure(0, weight=1)
        
        lang_button_frame = ctk.CTkFrame(self.settings_frame); lang_button_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ctk.CTkLabel(lang_button_frame, text="Language/语言:").pack(side="left", padx=10)
        self.lang_switch = ctk.CTkSegmentedButton(lang_button_frame, values=["中文", "English"]); self.lang_switch.pack(side="left", padx=10)

        self.settings_label = ctk.CTkLabel(self.settings_frame, image=self.settings_icon, compound="left", font=ctk.CTkFont(size=15, weight="bold")); self.settings_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        delimiter_frame = ctk.CTkFrame(self.settings_frame); delimiter_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5,10)); delimiter_frame.grid_columnconfigure(1, weight=1)
        self.delimiter_label = ctk.CTkLabel(delimiter_frame); self.delimiter_label.grid(row=0, column=0, padx=10, pady=5)
        self.delimiter_var = ctk.StringVar(); self.delimiter_options = ctk.CTkSegmentedButton(delimiter_frame, values=[",", "\\t", "|", ";"], variable=self.delimiter_var); self.delimiter_options.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.custom_delimiter_label = ctk.CTkLabel(delimiter_frame); self.custom_delimiter_label.grid(row=1, column=0, padx=10, pady=5)
        self.custom_delimiter_entry = ctk.CTkEntry(delimiter_frame, textvariable=self.delimiter_var); self.custom_delimiter_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        parser_config_frame = ctk.CTkFrame(self.settings_frame); parser_config_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5); parser_config_frame.grid_columnconfigure(1, weight=1); parser_config_frame.grid_columnconfigure(3, weight=1)
        self.header_row_var = ctk.StringVar(); self.header_row_label = ctk.CTkLabel(parser_config_frame); self.header_row_label.grid(row=0, column=0, padx=(10,0), pady=5); ctk.CTkEntry(parser_config_frame, textvariable=self.header_row_var, width=60).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.skip_rows_var = ctk.StringVar(); self.skip_rows_label = ctk.CTkLabel(parser_config_frame); self.skip_rows_label.grid(row=0, column=2, padx=(10,0), pady=5); ctk.CTkEntry(parser_config_frame, textvariable=self.skip_rows_var, width=60).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.quote_char_var = ctk.StringVar(); self.quote_char_label = ctk.CTkLabel(parser_config_frame); self.quote_char_label.grid(row=1, column=0, padx=(10,0), pady=5); self.quote_char_option_menu = ctk.CTkOptionMenu(parser_config_frame, variable=self.quote_char_var, values=['"', "'", _("no_quote_char")]); self.quote_char_option_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.cleaning_label = ctk.CTkLabel(self.settings_frame, font=ctk.CTkFont(weight="bold")); self.cleaning_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=5, pady=(15, 5))
        cleaning_frame = ctk.CTkFrame(self.settings_frame); cleaning_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=5); cleaning_frame.grid_columnconfigure((0,1), weight=1)
        self.remove_empty_button = ctk.CTkButton(cleaning_frame); self.remove_empty_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew"); self.remove_empty_tooltip = Tooltip(self.remove_empty_button, "")
        self.remove_duplicates_button = ctk.CTkButton(cleaning_frame); self.remove_duplicates_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew"); self.remove_duplicates_tooltip = Tooltip(self.remove_duplicates_button, "")
        self.normalize_columns_button = ctk.CTkButton(cleaning_frame); self.normalize_columns_button.grid(row=1, column=0, padx=5, pady=5, sticky="ew"); self.normalize_columns_tooltip = Tooltip(self.normalize_columns_button, "")
        fill_na_frame = ctk.CTkFrame(cleaning_frame); fill_na_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew"); fill_na_frame.grid_columnconfigure(0, weight=1)
        self.fill_na_entry = ctk.CTkEntry(fill_na_frame); self.fill_na_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.fill_na_button = ctk.CTkButton(fill_na_frame, width=80); self.fill_na_button.grid(row=0, column=1, padx=5, pady=5); self.fill_na_tooltip = Tooltip(self.fill_na_button, "")

        self.export_label = ctk.CTkLabel(self.settings_frame, font=ctk.CTkFont(weight="bold")); self.export_label.grid(row=6, column=0, columnspan=2, sticky="w", padx=5, pady=(15, 5))
        export_frame = ctk.CTkFrame(self.settings_frame); export_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=5); export_frame.grid_columnconfigure((0,1), weight=1)
        self.export_excel_button = ctk.CTkButton(export_frame); self.export_excel_button.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.export_csv_button = ctk.CTkButton(export_frame); self.export_csv_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.open_after_export_var = ctk.BooleanVar(); self.open_after_export_check = ctk.CTkCheckBox(export_frame, variable=self.open_after_export_var); self.open_after_export_check.grid(row=2, column=0, columnspan=2, padx=5, pady=10)

        self.preview_label = ctk.CTkLabel(self.right_frame, image=self.preview_icon, compound="left", font=ctk.CTkFont(size=15, weight="bold")); self.preview_label.grid(row=0, column=0, sticky="nw", padx=10, pady=5)
        self.tree = ttk.Treeview(self.right_frame, show="headings", selectmode="extended", style="Custom.Treeview"); self.tree.grid(row=0, column=0, sticky="nsew", padx=10, pady=(30, 10))
        preview_controls_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent"); preview_controls_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5); preview_controls_frame.grid_columnconfigure(0, weight=1); preview_controls_frame.grid_columnconfigure(1, weight=1)
        self.manage_columns_button = ctk.CTkButton(preview_controls_frame); self.manage_columns_button.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.delete_rows_button = ctk.CTkButton(preview_controls_frame, fg_color="red", hover_color="#c0392b"); self.delete_rows_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
    def update_ui_text(self):
        _ = get_translator().get
        self.master.title(_("app_title"))
        self.status_label.configure(text=_("status_ready"))
        self.input_label.configure(text=_("input_data_label"))
        self.hint_label.configure(text=_("hint_text"))
        self.example_data_button.configure(text=_("example_data_button"))
        self.settings_label.configure(text=_("settings_label"))
        self.delimiter_label.configure(text=_("delimiter_label"))
        self.custom_delimiter_label.configure(text=_("custom_delimiter_label"))
        self.header_row_label.configure(text=_("header_row_label"))
        self.skip_rows_label.configure(text=_("skip_rows_label"))
        self.quote_char_label.configure(text=_("quote_char_label"))
        self.quote_char_option_menu.configure(values=['"', "'", _("no_quote_char")])
        self.cleaning_label.configure(text=_("cleaning_label"))
        self.remove_empty_button.configure(text=_("remove_empty_rows_button"))
        self.remove_duplicates_button.configure(text=_("remove_duplicates_button"))
        self.normalize_columns_button.configure(text=_("normalize_columns_button"))
        self.fill_na_entry.configure(placeholder_text=_("fill_na_placeholder"))
        self.fill_na_button.configure(text=_("fill_na_button"))
        self.export_label.configure(text=_("export_label"))
        self.export_excel_button.configure(text=_("export_excel_button"))
        self.export_csv_button.configure(text=_("export_csv_button"))
        self.open_after_export_check.configure(text=_("open_after_export_check"))
        self.preview_label.configure(text=_("preview_label"))
        self.manage_columns_button.configure(text=_("manage_columns_button"))
        self.delete_rows_button.configure(text=_("delete_rows_button"))
        
        self.remove_empty_tooltip.text = _("tooltip_remove_empty")
        self.remove_duplicates_tooltip.text = _("tooltip_remove_duplicates")
        self.normalize_columns_tooltip.text = _("tooltip_normalize_columns")
        self.fill_na_tooltip.text = _("tooltip_fill_na")

    def on_treeview_double_click(self, event):
        if self._edit_entry:
            self._edit_entry.destroy()

        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
            
        item_id = self.tree.focus()
        column_index_str = self.tree.identify_column(event.x)
        
        if not item_id or not column_index_str:
            return

        x, y, width, height = self.tree.bbox(item_id, column_index_str)
        
        row_index = self.tree.index(item_id)
        column_name = self.tree.column(column_index_str, "id")
        
        column_int_index = int(column_index_str.replace("#", "")) - 1
        original_value = self.tree.item(item_id, "values")[column_int_index]

        self._edit_entry = ctk.CTkEntry(self.tree, border_width=0, corner_radius=0)
        self._edit_entry.place(x=x, y=y, width=width, height=height)
        
        self._edit_entry.insert(0, original_value)
        self._edit_entry.select_range(0, 'end')
        self._edit_entry.focus_set()

        self._edit_entry.bind("<Return>", lambda e, r=row_index, c=column_name: self.save_cell_edit(r, c, self._edit_entry.get()))
        self._edit_entry.bind("<FocusOut>", lambda e, r=row_index, c=column_name: self.save_cell_edit(r, c, self._edit_entry.get()))
        self._edit_entry.bind("<Escape>", lambda e: self._edit_entry.destroy())

    def save_cell_edit(self, row_index, column_name, new_value):
        if self._edit_entry:
            self._edit_entry.destroy()
            self._edit_entry = None
            self.controller.on_cell_update(row_index, column_name, new_value)
            
    def _debounce_input(self, *args):
        if self._debounce_timer:
            self.after_cancel(self._debounce_timer)
        self._debounce_timer = self.after(500, self.controller.process_input_data)

    def update_preview(self, df):
        if self._edit_entry:
            self._edit_entry.destroy()
            self._edit_entry = None

        for i in self.tree.get_children():
            self.tree.delete(i)
        
        self.tree["columns"] = list(df.columns)
        for col in df.columns:
            self.tree.heading(col, text=col, anchor='w')
            self.tree.column(col, anchor="w", width=120, minwidth=60, stretch=True)
            
        for index, row in df.iterrows():
            self.tree.insert("", "end", values=list(row.astype(str)))
        
        total_rows = len(df)
        total_cols = len(df.columns)
        if self.controller:
             self.update_status(self.controller._("status_preview").format(rows=total_rows, cols=total_cols))

    def update_status(self, text):
        self.status_label.configure(text=text)
    
    def add_history(self, text):
        self.history_log.configure(state="normal")
        self.history_log.insert("end", text + "\n")
        self.history_log.configure(state="disabled")
        self.history_log.yview_moveto(1.0)
        
    def update_treeview_style(self, event=None):
        fg_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        text_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        selected_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"])

        self.style.theme_use("default")
        self.style.configure("Treeview", background=fg_color, foreground=text_color, fieldbackground=fg_color, borderwidth=0, rowheight=25)
        self.style.map('Treeview', background=[('selected', selected_color)], foreground=[('selected', text_color)])
        self.style.configure("Treeview.Heading", background=fg_color, foreground=text_color, font=('Segoe UI', 10, 'bold'), borderwidth=0)
        self.style.map("Treeview.Heading", background=[('active', fg_color)])
        
        # Check if the binding already exists before adding it
        if "update_treeview_style" not in str(self.master.bind("<<ThemeChanged>>")):
            self.master.bind("<<ThemeChanged>>", self.update_treeview_style, add="+")

    def _load_icon(self, name, size=(24, 24)):
        try:
            image_path = os.path.join(self.icon_path, name)
            return ctk.CTkImage(Image.open(image_path), size=size)
        except FileNotFoundError:
            logging.warning(f"Icon not found: {os.path.join(self.icon_path, name)}")
            return None

    def get_settings(self):
        return {
            "delimiter": self.delimiter_var.get(),
            "header_row": self.header_row_var.get(),
            "skip_rows": self.skip_rows_var.get(),
            "quote_char": self.quote_char_var.get(),
            "open_after_export": self.open_after_export_var.get()
        }

    def set_settings(self, settings):
        self.delimiter_var.set(settings.get("delimiter", ","))
        self.header_row_var.set(settings.get("header_row", "0"))
        self.skip_rows_var.set(settings.get("skip_rows", "0"))
        self.quote_char_var.set(settings.get("quote_char", '"'))
        self.open_after_export_var.set(settings.get("open_after_export", True)) 