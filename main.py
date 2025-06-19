import customtkinter as ctk
from app_view import AppView
from app_controller import AppController
from data_model import DataModel
from i18n import translator, get_translator
import logging
import os

def setup_logging():
    """配置日志记录，同时输出到文件和控制台"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "app.log"), encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def main():
    setup_logging()
    logging.info("应用启动")
    
    # 设置主题
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    # 按照MVC模式初始化
    model = DataModel()
    view = AppView(model) 
    controller = AppController(model, view)
    view.set_controller(controller)
    
    controller.run() # run()方法包含mainloop

if __name__ == "__main__":
    main() 