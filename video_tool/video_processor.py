# 视频处理模块
from common.Logger import get_logger
logger = get_logger("视频处理")

from typing import Optional
import cv2
from PIL import Image
import math
import numpy as np

class VideoProcessor:
    def __init__(self):
        pass
    
    def load_video(self, file_path: str) -> cv2.VideoCapture:
        """加载视频文件"""
        logger.info(f"加载视频: {file_path}")
        try:
            video = cv2.VideoCapture(file_path)
            if not video.isOpened():
                raise Exception("无法打开视频文件")
            
            # 获取视频信息
            fps = video.get(cv2.CAP_PROP_FPS)
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            logger.info(f"视频信息: FPS={fps:.2f}, 总帧数={total_frames}, 分辨率={width}x{height}")
            return video
        except Exception as e:
            logger.error(f"视频加载失败: {e}")
            raise
    
    def get_video_info(self, video: cv2.VideoCapture) -> dict:
        """获取视频信息"""
        try:
            fps = video.get(cv2.CAP_PROP_FPS)
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            return {
                "fps": fps,
                "total_frames": total_frames,
                "width": width,
                "height": height
            }
        except Exception as e:
            logger.error(f"获取视频信息失败: {e}")
            raise
    
    def extract_frames(self, video: cv2.VideoCapture, target_fps: float, max_frames: Optional[int] = None) -> list[Image.Image]:
        """根据目标帧率提取视频帧"""
        logger.info(f"开始提取视频帧，目标帧率: {target_fps}")
        
        try:
            # 获取视频信息
            video_info = self.get_video_info(video)
            original_fps = video_info["fps"]
            total_frames = video_info["total_frames"]
            
            # 计算帧间隔
            frame_interval = int(original_fps / target_fps)
            logger.info(f"原始帧率: {original_fps:.2f}, 帧间隔: {frame_interval}")
            
            frames = []
            current_frame = 0
            frame_count = 0
            
            while True:
                # 设置当前帧位置
                video.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
                
                # 读取帧
                ret, frame = video.read()
                if not ret:
                    break
                
                # 转换为PIL Image
                # OpenCV读取的帧是BGR格式，需要转换为RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                frames.append(pil_image)
                
                frame_count += 1
                current_frame += frame_interval
                
                # 检查是否达到最大帧数限制
                if max_frames and frame_count >= max_frames:
                    logger.info(f"达到最大帧数限制: {max_frames}")
                    break
                
                # 检查是否超出视频总帧数
                if current_frame >= total_frames:
                    break
            
            logger.info(f"帧提取完成，共提取 {len(frames)} 帧")
            return frames
        except Exception as e:
            logger.error(f"帧提取失败: {e}")
            raise
    
    def resize_frame(self, frame: Image.Image, max_pixels: int) -> Image.Image:
        """保持长宽比缩放帧到指定最大像素数"""
        original_width, original_height = frame.size
        original_pixels = original_width * original_height
        
        logger.debug(f"原始帧尺寸: {original_width}x{original_height}，像素数: {original_pixels}")
        logger.debug(f"目标最大像素数: {max_pixels}")
        
        if original_pixels <= max_pixels:
            logger.debug("帧像素数已小于目标值，无需缩放")
            return frame
        
        # 计算缩放比例
        scale = math.sqrt(max_pixels / original_pixels)
        logger.debug(f"计算缩放比例: {scale:.6f}")
        
        # 计算新尺寸
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        # 确保尺寸至少为1x1
        new_width = max(1, new_width)
        new_height = max(1, new_height)
        
        logger.debug(f"缩放后帧尺寸: {new_width}x{new_height}，像素数: {new_width * new_height}")
        
        # 缩放帧
        resized_frame = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
        logger.debug("帧缩放成功")
        
        return resized_frame
    
    def process_frame(self, frame: Image.Image, max_pixels: int) -> tuple[list[list[tuple]], int, int]:
        """处理单帧，返回像素数据、宽度和高度"""
        logger.debug("开始处理帧")
        
        # 缩放帧
        resized_frame = self.resize_frame(frame, max_pixels)
        
        # 转换为RGBA模式
        rgba_frame = resized_frame.convert("RGBA")
        
        # 获取像素数据
        width, height = rgba_frame.size
        pixel_data = []
        
        for y in range(height):
            row = []
            for x in range(width):
                pixel = rgba_frame.getpixel((x, y))
                row.append(pixel)
            pixel_data.append(row)
        
        logger.debug(f"帧处理完成，最终尺寸: {width}x{height}")
        return pixel_data, width, height
    
    def calculate_frame_difference(self, frame1: Image.Image, frame2: Image.Image) -> float:
        """计算两帧之间的差异值"""
        try:
            # 确保两帧尺寸相同
            if frame1.size != frame2.size:
                frame2 = frame2.resize(frame1.size, Image.Resampling.LANCZOS)
            
            # 转换为numpy数组
            arr1 = np.array(frame1)
            arr2 = np.array(frame2)
            
            # 计算差异
            diff = np.abs(arr1.astype(np.float32) - arr2.astype(np.float32))
            mean_diff = np.mean(diff)
            return float(mean_diff)
        except Exception as e:
            logger.error(f"计算帧差异失败: {e}")
            return float('inf')
    
    def process_video(self, file_path: str, target_fps: float, max_pixels: int, max_frames: Optional[int] = None) -> list[tuple[list[list[tuple]], int, int]]:
        """完整处理视频，返回处理后的帧序列"""
        logger.info(f"开始处理视频: {file_path}")
        
        try:
            # 使用生成器版本处理视频
            processed_frames = list(self.process_video_generator(file_path, target_fps, max_pixels, max_frames))
            logger.info("视频处理完成")
            return processed_frames
        except Exception as e:
            logger.error(f"视频处理失败: {e}")
            raise
    
    def process_video_generator(self, file_path: str, target_fps: float, max_pixels: int, max_frames: Optional[int] = None):
        """使用生成器模式处理视频，逐帧处理，减少内存使用"""
        import psutil
        import gc
        
        logger.info(f"开始流式处理视频: {file_path}")
        
        try:
            # 加载视频
            video = self.load_video(file_path)
            
            # 获取视频信息
            video_info = self.get_video_info(video)
            original_fps = video_info["fps"]
            total_frames = video_info["total_frames"]
            
            # 计算帧间隔
            frame_interval = int(original_fps / target_fps)
            logger.info(f"原始帧率: {original_fps:.2f}, 帧间隔: {frame_interval}")
            
            current_frame = 0
            frame_count = 0
            
            while True:
                # 监控内存使用
                if frame_count % 10 == 0:
                    memory = psutil.virtual_memory()
                    logger.debug(f"内存使用: {memory.percent:.1f}%, 已处理帧: {frame_count}")
                    
                    # 如果内存使用过高，进行垃圾回收
                    if memory.percent > 80:
                        logger.warning(f"内存使用过高: {memory.percent:.1f}%, 执行垃圾回收")
                        gc.collect()
                        memory = psutil.virtual_memory()
                        logger.info(f"垃圾回收后内存使用: {memory.percent:.1f}%")
                
                # 设置当前帧位置
                video.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
                
                # 读取帧
                ret, frame = video.read()
                if not ret:
                    break
                
                # 转换为PIL Image
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(frame_rgb)
                
                # 处理帧
                logger.info(f"处理第 {frame_count+1} 帧")
                pixel_data, width, height = self.process_frame(pil_image, max_pixels)
                
                # 生成处理结果
                yield (pixel_data, width, height)
                
                # 释放不再使用的帧数据
                del frame
                del frame_rgb
                del pil_image
                del pixel_data
                
                # 每处理几帧后进行一次垃圾回收
                if frame_count % 5 == 0:
                    gc.collect()
                
                frame_count += 1
                current_frame += frame_interval
                
                # 检查是否达到最大帧数限制
                if max_frames and frame_count >= max_frames:
                    logger.info(f"达到最大帧数限制: {max_frames}")
                    break
                
                # 检查是否超出视频总帧数
                if current_frame >= total_frames:
                    break
            
            # 释放视频
            video.release()
            # 最后进行一次垃圾回收
            gc.collect()
            logger.info(f"流式处理完成，共处理 {frame_count} 帧")
        except Exception as e:
            logger.error(f"视频处理失败: {e}")
            # 确保视频被释放
            video_capture = locals().get('video')
            if video_capture:
                try:
                    video_capture.release()
                except:
                    pass
            raise