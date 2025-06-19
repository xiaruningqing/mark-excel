import customtkinter as ctk
from app_view import AppView
from app_controller import AppController
from data_model import DataModel
from tkinterdnd2 import TkinterDnD
import logging

def setup_logging():
    """配置日志记录，同时输出到文件和控制台"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def main():
    setup_logging()
    logging.info("应用启动")
    
    # 1. 创建一个隐藏的、DND-aware的根窗口
    dnd_root = TkinterDnD.Tk()
    dnd_root.withdraw()

    # 2. 创建一个CTkToplevel作为我们的主窗口
    root = ctk.CTkToplevel(dnd_root)
    root.title("表格数据整理工具")
    root.geometry("1200x800")
    
    # 设置主题
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    # 3. 将AppView作为Frame嵌入到主窗口中
    view = AppView(master=root)
    model = DataModel()
    controller = AppController(model, view)
    view.set_controller(controller)

    # 4. 加载配置
    controller.load_config()
    
    # 5. 定义关闭行为
    def on_closing():
        logging.info("应用关闭")
        controller.save_config()
        dnd_root.destroy() # 必须销毁根窗口

    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 6. 在DND根窗口上运行主循环
    dnd_root.mainloop()

if __name__ == "__main__":
    main() 