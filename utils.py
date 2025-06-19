import customtkinter as ctk
import csv
from io import StringIO

def detect_delimiter(text_data, max_lines=20):
    """
    Intelligently detects the delimiter for a given text data.
    """
    try:
        # Use a small sample of the data to perform detection
        sniffer = csv.Sniffer()
        sample = "\n".join(text_data.splitlines()[:max_lines])
        delimiter = sniffer.sniff(sample).delimiter
        return delimiter
    except csv.Error:
        # Fallback for when sniffer fails (e.g., single column data)
        if '\t' in sample:
            return '\t'
        if '|' in sample:
            return '|'
        if ';' in sample:
            return ';'
        if ',' in sample:
            return ','
        return ',' # Default fallback

class Tooltip:
    def __init__(self, widget, text, show_delay=400, hide_delay=100):
        self.widget = widget
        self.text = text
        self.show_delay = show_delay  # ms
        self.hide_delay = hide_delay  # ms
        self.tooltip_window = None
        self.id = None
        self.widget.bind("<Enter>", self.schedule_show)
        self.widget.bind("<Leave>", self.schedule_hide)
        self.widget.bind("<ButtonPress>", self.schedule_hide)

    def schedule_show(self, event=None):
        self.cancel_scheduled_hide() # Cancel any pending hide requests
        if self.tooltip_window: # If tooltip is already shown, do nothing
            return
        self.id = self.widget.after(self.show_delay, self.show_tooltip)

    def schedule_hide(self, event=None):
        self.cancel_scheduled_show() # Cancel any pending show requests
        if self.tooltip_window:
            self.id = self.widget.after(self.hide_delay, self.hide_tooltip)
        
    def cancel_scheduled_show(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
            
    def cancel_scheduled_hide(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show_tooltip(self, event=None):
        if self.tooltip_window:
            return
        
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        self.tooltip_window = ctk.CTkToplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        # Use a frame to get the desired background and border
        frame = ctk.CTkFrame(self.tooltip_window, corner_radius=5, border_width=1)
        frame.pack()

        label = ctk.CTkLabel(frame, text=self.text, corner_radius=5,
                             text_color=("gray10", "gray90"),
                             wraplength=250)
        label.pack(ipadx=5, ipady=3)

    def hide_tooltip(self, event=None):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None 