# 主程序入口
import os
from common.Logger import get_logger
logger = get_logger("主程序")

import ttkbootstrap as ttk
from ttkbootstrap.constants import *  # pyright: ignore[reportWildcardImportFromLibrary]
from ttkbootstrap.dialogs import Messagebox
from tkinter import filedialog
import threading
from io import StringIO

from image_tool.image_processor import ImageProcessor
from image_tool.adofai_generator import ADOFAIGenerator

class ImageToADOFaiApp:
    def __init__(self):
        # 创建主窗口
        self.root = ttk.Window(themename="darkly")
        self.root.title("图片转ADOFai关卡")
        self.root.geometry("800x600")
        
        # 初始化变量
        self.image_path = ""
        self.max_pixels = 300000  # 默认3*10^5像素
        self.output_path = ""
        
        # 初始化图片处理器
        self.image_processor = ImageProcessor()
        
        # 创建UI组件
        self.create_widgets()
    
    def create_widgets(self):
        """创建UI组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # 图片选择
        image_frame = ttk.Labelframe(main_frame, text="图片选择", padding=10)
        image_frame.pack(fill=X, pady=5)
        
        self.image_entry = ttk.Entry(image_frame)
        self.image_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)
        
        ttk.Button(
            image_frame, 
            text="浏览", 
            command=self.select_image,
            bootstyle="primary"
        ).pack(side=RIGHT, padx=5)
        
        # 最大像素设置
        pixels_frame = ttk.Labelframe(main_frame, text="最大像素数", padding=10)
        pixels_frame.pack(fill=X, pady=5)
        
        ttk.Label(pixels_frame, text="最大像素数: ").pack(side=LEFT, padx=5)
        
        self.pixels_entry = ttk.Entry(pixels_frame, width=15)
        self.pixels_entry.insert(0, str(self.max_pixels))
        self.pixels_entry.pack(side=LEFT, padx=5)
        
        ttk.Label(pixels_frame, text="(例如：300000表示3*10^5像素)").pack(side=LEFT, padx=5)
        
        # 输出路径选择
        output_frame = ttk.Labelframe(main_frame, text="输出路径", padding=10)
        output_frame.pack(fill=X, pady=5)
        
        self.output_entry = ttk.Entry(output_frame)
        self.output_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)
        
        ttk.Button(
            output_frame, 
            text="浏览", 
            command=self.select_output,
            bootstyle="primary"
        ).pack(side=RIGHT, padx=5)
        
        # 转换按钮
        button_frame = ttk.Frame(main_frame, padding=10)
        button_frame.pack(fill=X, pady=5)
        
        self.convert_button = ttk.Button(
            button_frame, 
            text="开始转换", 
            command=self.start_conversion,
            bootstyle="success",
            width=20
        )
        self.convert_button.pack(side=LEFT, padx=5)
    
    def select_image(self):
        """选择图片文件"""
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[
                ("图片文件", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            self.image_path = file_path
            self.image_entry.delete(0, END)
            self.image_entry.insert(0, self.image_path)
            logger.info(f"选择图片: {self.image_path}")
    
    def select_output(self):
        """选择输出文件路径"""
        file_path = filedialog.asksaveasfilename(
            title="保存ADOFai关卡",
            defaultextension=".adofai",
            filetypes=[
                ("ADOFai关卡文件", "*.adofai"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            self.output_path = file_path
            self.output_entry.delete(0, END)
            self.output_entry.insert(0, self.output_path)
            logger.info(f"选择输出路径: {self.output_path}")
    
    def validate_input(self):
        """验证输入是否有效"""
        self.image_path = self.image_entry.get().strip().replace('"', '')
        self.output_path = self.output_entry.get().strip().replace('"', '')
        if not self.image_path:
            Messagebox.show_error("请选择图片文件", "错误")
            return False
        
        try:
            self.max_pixels = int(self.pixels_entry.get())
            if self.max_pixels <= 0:
                raise ValueError("最大像素数必须大于0")
        except ValueError as e:
            Messagebox.show_error(f"无效的最大像素数: {e}", "错误")
            return False
        
        if not self.output_path:
            self.output_path = "output.adofai"
            self.output_entry.delete(0, END)
            self.output_entry.insert(0, self.output_path)
            logger.info(f"默认输出路径: {self.output_path}")
        
        return True
    
    def start_conversion(self):
        """开始转换过程"""
        if not self.validate_input():
            return
        
        # 禁用转换按钮，防止重复点击
        self.convert_button.configure(state="disabled")
        
        # 在新线程中执行转换，避免阻塞UI
        threading.Thread(target=self.convert, daemon=True).start()
    
    def convert(self):
        """执行转换过程"""
        try:
            logger.info("开始转换图片到ADOFai关卡")
            
            # 处理图片
            pixel_data, width, height = self.image_processor.process_image(
                self.image_path, 
                self.max_pixels
            )
            
            # 生成关卡
            generator = ADOFAIGenerator(pixel_data, width, height)
            generator.generate_and_save(self.output_path)
            
            logger.info("转换完成！")
            
            # 显示成功消息
            self.root.after(0, lambda: 
                Messagebox.show_info(
                    f"转换完成！\n\n" \
                    f"原始图片尺寸: {self.image_processor.load_image(self.image_path).width}x{self.image_processor.load_image(self.image_path).height}\n" \
                    f"缩放后尺寸: {width}x{height}\n" \
                    f"总砖块数: {width * height}\n" \
                    f"输出文件: {self.output_path}", \
                    "成功"
                )
            )
        except Exception as e:
            logger.error(f"转换失败: {e}")
            
            # 显示错误消息
            self.root.after(0, lambda: 
                Messagebox.show_error(f"转换失败: {e}", "错误")
            )
        finally:
            # 重新启用转换按钮
            self.root.after(0, lambda: 
                self.convert_button.configure(state="normal")
            )
    
    def run(self):
        """运行应用程序"""
        logger.info("启动应用程序")
        self.root.mainloop()

if __name__ == "__main__":
    app = ImageToADOFaiApp()
    app.run()
