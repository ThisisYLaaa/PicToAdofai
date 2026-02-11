# 视频转ADOFAI工具主界面
import os
from common.Logger import get_logger
logger = get_logger("视频转ADOFAI主界面")

import ttkbootstrap as ttk
from ttkbootstrap.constants import BOTH, YES, LEFT, RIGHT, X, Y
from ttkbootstrap.dialogs import Messagebox
from tkinter import filedialog, Label, W, END
import threading
from PIL import Image, ImageTk
import cv2

from video_tool.video_processor import VideoProcessor
from video_tool.torch_video_processor import TorchVideoProcessor
from video_tool.video_to_adofai import VideoToADOFAI

class VideoToADOFAIApp:
    def __init__(self):
        """初始化视频转ADOFAI应用"""
        # 创建主窗口
        self.root = ttk.Window(themename="darkly")
        self.root.title("视频转ADOFAI关卡")
        self.root.geometry("1000x700")
        
        # 初始化变量
        self.video_path = ""
        self.target_fps = 10.0  # 默认目标帧率
        self.diff_threshold = 10.0  # 默认颜色差异阈值
        self.max_frames = 100  # 默认最大帧数
        self.max_pixels = 300000  # 默认最大像素数
        self.output_path = ""
        self.processor_type = "pytorch"  # 默认使用PyTorch处理器
        
        # 初始化处理器
        self.video_processor = None
        self.torch_video_processor = None
        self.video_to_adofai = VideoToADOFAI()
        
        # 初始化处理器实例
        self._init_processors()
        
        # 预览相关
        self.preview_frame = None
        self.preview_label = None
        
        # 创建UI组件
        self.create_widgets()
    
    def _init_processors(self):
        """初始化处理器实例"""
        try:
            # 初始化PyTorch处理器
            self.torch_video_processor = TorchVideoProcessor()
            logger.info("PyTorch处理器初始化成功")
            
            # 初始化传统处理器
            self.video_processor = VideoProcessor()
            logger.info("传统处理器初始化成功")
            
            # 根据处理器类型选择当前处理器
            self._select_processor()
        except Exception as e:
            logger.error(f"处理器初始化失败: {e}")
            # 至少确保传统处理器可用
            try:
                self.video_processor = VideoProcessor()
                self.processor_type = "traditional"
                self.current_processor = self.video_processor
                logger.info("仅传统处理器初始化成功")
            except Exception as e2:
                logger.error(f"传统处理器初始化也失败: {e2}")
                self.current_processor = None
    
    def _select_processor(self):
        """选择当前处理器"""
        if self.processor_type == "pytorch" and self.torch_video_processor:
            self.current_processor = self.torch_video_processor
            logger.info("使用PyTorch处理器")
        else:
            self.current_processor = self.video_processor
            logger.info("使用传统处理器")
    
    def _on_processor_change(self):
        """处理处理器类型变更"""
        new_type = self.processor_var.get()
        if new_type != self.processor_type:
            self.processor_type = new_type
            self._select_processor()
            logger.info(f"处理器类型已更改为: {new_type}")
    
    def create_widgets(self):
        """创建UI组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)
        
        # 创建左侧控制面板
        control_frame = ttk.Frame(main_frame, padding=10)
        control_frame.pack(side=LEFT, fill=Y, padx=10)
        
        # 视频选择
        video_frame = ttk.Labelframe(control_frame, text="视频选择", padding=10)
        video_frame.pack(fill=X, pady=5)
        
        self.video_entry = ttk.Entry(video_frame)
        self.video_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)
        
        ttk.Button(
            video_frame, 
            text="浏览", 
            command=self.select_video,
            bootstyle="primary"
        ).pack(side=RIGHT, padx=5)
        
        # 处理器选择
        processor_frame = ttk.Labelframe(control_frame, text="处理器选择", padding=10)
        processor_frame.pack(fill=X, pady=5)
        
        ttk.Label(processor_frame, text="处理引擎: ").pack(side=LEFT, padx=5)
        
        self.processor_var = ttk.StringVar(value=self.processor_type)
        processor_frame_inner = ttk.Frame(processor_frame)
        processor_frame_inner.pack(side=LEFT, padx=5)
        
        ttk.Radiobutton(
            processor_frame_inner, 
            text="PyTorch (GPU加速)", 
            variable=self.processor_var, 
            value="pytorch",
            command=self._on_processor_change
        ).pack(anchor=W, pady=2)
        
        ttk.Radiobutton(
            processor_frame_inner, 
            text="传统 (CPU)", 
            variable=self.processor_var, 
            value="traditional",
            command=self._on_processor_change
        ).pack(anchor=W, pady=2)
        
        # 视频参数设置
        params_frame = ttk.Labelframe(control_frame, text="视频参数", padding=10)
        params_frame.pack(fill=X, pady=5)
        
        # 帧速率设置
        ttk.Label(params_frame, text="目标帧率 (fps): ").pack(side=LEFT, padx=5)
        self.fps_entry = ttk.Entry(params_frame, width=10)
        self.fps_entry.insert(0, str(self.target_fps))
        self.fps_entry.pack(side=LEFT, padx=5)
        
        # 颜色差异阈值设置
        ttk.Label(params_frame, text="颜色差异阈值: ").pack(side=LEFT, padx=5)
        self.diff_entry = ttk.Entry(params_frame, width=10)
        self.diff_entry.insert(0, str(self.diff_threshold))
        self.diff_entry.pack(side=LEFT, padx=5)
        
        # 最大帧数设置
        ttk.Label(params_frame, text="最大帧数: ").pack(side=LEFT, padx=5)
        self.max_frames_entry = ttk.Entry(params_frame, width=10)
        self.max_frames_entry.insert(0, str(self.max_frames))
        self.max_frames_entry.pack(side=LEFT, padx=5)
        
        # 最大像素数设置
        pixels_frame = ttk.Labelframe(control_frame, text="图像参数", padding=10)
        pixels_frame.pack(fill=X, pady=5)
        
        ttk.Label(pixels_frame, text="最大像素数: ").pack(side=LEFT, padx=5)
        self.pixels_entry = ttk.Entry(pixels_frame, width=15)
        self.pixels_entry.insert(0, str(self.max_pixels))
        self.pixels_entry.pack(side=LEFT, padx=5)
        
        # 输出路径选择
        output_frame = ttk.Labelframe(control_frame, text="输出路径", padding=10)
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
        button_frame = ttk.Frame(control_frame, padding=10)
        button_frame.pack(fill=X, pady=5)
        
        self.convert_button = ttk.Button(
            button_frame, 
            text="开始转换", 
            command=self.start_conversion,
            bootstyle="success",
            width=20
        )
        self.convert_button.pack(side=LEFT, padx=5)
        
        self.preview_button = ttk.Button(
            button_frame, 
            text="预览第一帧", 
            command=self.preview_first_frame,
            bootstyle="info",
            width=15
        )
        self.preview_button.pack(side=LEFT, padx=5)
        
        # 进度条
        progress_frame = ttk.Labelframe(control_frame, text="转换进度", padding=10)
        progress_frame.pack(fill=X, pady=5)
        
        self.progress_var = ttk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var, 
            maximum=100, 
            length=300
        )
        self.progress_bar.pack(fill=X, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="就绪")
        self.progress_label.pack(fill=X, pady=5)
        
        # 创建右侧预览面板
        preview_frame = ttk.Labelframe(main_frame, text="预览", padding=10)
        preview_frame.pack(side=RIGHT, fill=BOTH, expand=YES, padx=10)
        
        # 预览标签
        self.preview_label = Label(preview_frame, text="视频预览将显示在这里")
        self.preview_label.pack(fill=BOTH, expand=YES)
    
    def select_video(self):
        """选择视频文件"""
        file_path = filedialog.askopenfilename(
            title="选择视频",
            filetypes=[
                ("视频文件", "*.mp4;*.avi;*.mov;*.wmv;*.mkv"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            self.video_path = file_path
            self.video_entry.delete(0, END)
            self.video_entry.insert(0, self.video_path)
            logger.info(f"选择视频: {self.video_path}")
    
    def select_output(self):
        """选择输出文件路径"""
        file_path = filedialog.asksaveasfilename(
            title="保存ADOFAI关卡",
            defaultextension=".adofai",
            filetypes=[
                ("ADOFAI关卡文件", "*.adofai"),
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
        self.video_path = self.video_entry.get().strip().replace('"', '')
        self.output_path = self.output_entry.get().strip().replace('"', '')
        
        if not self.video_path:
            Messagebox.show_error("请选择视频文件", "错误")
            return False
        
        try:
            self.target_fps = float(self.fps_entry.get())
            if self.target_fps <= 0:
                raise ValueError("目标帧率必须大于0")
        except ValueError as e:
            Messagebox.show_error(f"无效的目标帧率: {e}", "错误")
            return False
        
        try:
            self.diff_threshold = float(self.diff_entry.get())
            if self.diff_threshold < 0:
                raise ValueError("颜色差异阈值不能为负数")
        except ValueError as e:
            Messagebox.show_error(f"无效的颜色差异阈值: {e}", "错误")
            return False
        
        try:
            self.max_frames = int(self.max_frames_entry.get())
            if self.max_frames <= 0:
                raise ValueError("最大帧数必须大于0")
        except ValueError as e:
            Messagebox.show_error(f"无效的最大帧数: {e}", "错误")
            return False
        
        try:
            self.max_pixels = int(self.pixels_entry.get())
            if self.max_pixels <= 0:
                raise ValueError("最大像素数必须大于0")
        except ValueError as e:
            Messagebox.show_error(f"无效的最大像素数: {e}", "错误")
            return False
        
        if not self.output_path:
            self.output_path = "video_output.adofai"
            self.output_entry.delete(0, END)
            self.output_entry.insert(0, self.output_path)
            logger.info(f"默认输出路径: {self.output_path}")
        
        return True
    
    def preview_first_frame(self):
        """预览视频的第一帧"""
        if not self.video_path:
            Messagebox.show_error("请先选择视频文件", "错误")
            return
        
        try:
            logger.info("开始预览第一帧")
            
            # 打开视频
            video = cv2.VideoCapture(self.video_path)
            if not video.isOpened():
                raise Exception("无法打开视频文件")
            
            # 读取第一帧
            ret, frame = video.read()
            if not ret:
                raise Exception("无法读取视频帧")
            
            # 转换为RGB格式
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 转换为PIL Image
            pil_image = Image.fromarray(frame_rgb)
            
            # 调整尺寸以适应预览窗口
            preview_width = 400
            preview_height = 300
            pil_image = pil_image.resize((preview_width, preview_height), Image.Resampling.LANCZOS)
            
            # 转换为Tkinter PhotoImage
            self.preview_frame = ImageTk.PhotoImage(pil_image)
            
            # 更新预览标签
            if self.preview_label:
                self.preview_label.config(image=self.preview_frame, text="")
                # 保持引用以防止垃圾回收
                self._preview_image_ref = self.preview_frame
            
            # 释放视频
            video.release()
            
            logger.info("第一帧预览成功")
        except Exception as e:
            logger.error(f"预览失败: {e}")
            Messagebox.show_error(f"预览失败: {e}", "错误")
    
    def start_conversion(self):
        """开始转换过程"""
        if not self.validate_input():
            return
        
        # 禁用转换按钮，防止重复点击
        self.convert_button.configure(state="disabled")
        self.preview_button.configure(state="disabled")
        
        # 在新线程中执行转换，避免阻塞UI
        threading.Thread(target=self.convert, daemon=True).start()
    
    def update_progress(self, value, text):
        """更新进度条"""
        self.progress_var.set(value)
        self.progress_label.config(text=text)
    
    def convert(self):
        """执行转换过程"""
        try:
            logger.info("开始转换视频到ADOFAI关卡")
            
            # 更新进度
            self.root.after(0, lambda: self.update_progress(10, "加载视频..."))
            
            # 确保处理器已初始化
            if not hasattr(self, 'current_processor') or self.current_processor is None:
                self._init_processors()
            
            # 使用当前选择的处理器
            current_processor = self.current_processor
            logger.info(f"使用处理器类型: {self.processor_type}")
            
            # 更新进度
            self.root.after(0, lambda: self.update_progress(20, "提取视频帧..."))
            
            # 使用生成器模式处理视频，逐帧处理
            processed_frames = []
            frame_count = 0
            
            # 检查处理器是否可用
            if not current_processor:
                raise Exception("视频处理器初始化失败，请检查日志")
            
            # 检查处理器是否支持生成器方法
            if hasattr(current_processor, 'process_video_generator'):
                logger.info("使用流式处理模式")
                
                # 使用生成器逐帧处理
                for i, frame_data in enumerate(current_processor.process_video_generator(
                    self.video_path, 
                    self.target_fps, 
                    self.max_pixels, 
                    self.max_frames
                )):
                    processed_frames.append(frame_data)
                    frame_count = i + 1
                    
                    # 更新进度
                    progress = 20 + (frame_count / (self.max_frames or 100)) * 30
                    progress = min(50, progress)
                    self.root.after(0, lambda i=frame_count: self.update_progress(progress, f"处理第 {i} 帧..."))
            else:
                # 回退到传统处理方式
                logger.info("使用传统处理模式")
                processed_frames = current_processor.process_video(
                    self.video_path, 
                    self.target_fps, 
                    self.max_pixels, 
                    self.max_frames
                )
                frame_count = len(processed_frames)
                self.root.after(0, lambda: self.update_progress(50, f"处理完成 {frame_count} 帧"))
            
            # 生成关卡
            self.root.after(0, lambda: self.update_progress(70, "生成ADOFAI关卡..."))
            
            video_to_adofai = VideoToADOFAI()
            success = video_to_adofai.convert(
                processed_frames, 
                self.target_fps, 
                self.output_path, 
                self.diff_threshold
            )
            
            # 更新进度
            self.root.after(0, lambda: self.update_progress(100, "转换完成！"))
            
            logger.info("转换完成！")
            
            # 显示成功消息
            self.root.after(0, lambda: 
                Messagebox.show_info(
                    f"转换完成！\n\n" \
                    f"视频: {os.path.basename(self.video_path)}\n" \
                    f"提取帧数: {len(processed_frames)}\n" \
                    f"目标帧率: {self.target_fps} fps\n" \
                    f"输出文件: {self.output_path}", \
                    "成功"
                )
            )
        except Exception as e:
            logger.error(f"转换失败: {e}")
            
            # 更新进度
            self.root.after(0, lambda: self.update_progress(0, "转换失败"))
            
            # 显示错误消息
            self.root.after(0, lambda: 
                Messagebox.show_error(f"转换失败: {e}", "错误")
            )
        finally:
            # 重新启用按钮
            self.root.after(0, lambda: self.convert_button.configure(state="normal"))
            self.root.after(0, lambda: self.preview_button.configure(state="normal"))
    
    def run(self):
        """运行应用程序"""
        logger.info("启动视频转ADOFAI应用")
        self.root.mainloop()

if __name__ == "__main__":
    app = VideoToADOFAIApp()
    app.run()