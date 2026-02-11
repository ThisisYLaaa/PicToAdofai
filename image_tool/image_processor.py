# 图片处理模块
from common.Logger import get_logger
logger = get_logger("图片处理")

from PIL import Image
import math

class ImageProcessor:
    def __init__(self):
        pass
    
    def load_image(self, file_path: str) -> Image.Image:
        """加载图片"""
        logger.info(f"加载图片: {file_path}")
        try:
            image = Image.open(file_path)
            # 转换为RGBA模式
            image = image.convert("RGBA")
            logger.debug(f"图片加载成功，尺寸: {image.width}x{image.height}，模式: {image.mode}")
            return image
        except Exception as e:
            logger.error(f"图片加载失败: {e}")
            raise
    
    def resize_image(self, image: Image.Image, max_pixels: int) -> Image.Image:
        """保持长宽比缩放图片到指定最大像素数"""
        original_width, original_height = image.size
        original_pixels = original_width * original_height
        
        logger.info(f"原始图片尺寸: {original_width}x{original_height}，像素数: {original_pixels}")
        logger.info(f"目标最大像素数: {max_pixels}")
        
        if original_pixels <= max_pixels:
            logger.debug("图片像素数已小于目标值，无需缩放")
            return image
        
        # 计算缩放比例
        scale = math.sqrt(max_pixels / original_pixels)
        logger.debug(f"计算缩放比例: {scale:.6f}")
        
        # 计算新尺寸
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        # 确保尺寸至少为1x1
        new_width = max(1, new_width)
        new_height = max(1, new_height)
        
        logger.info(f"缩放后图片尺寸: {new_width}x{new_height}，像素数: {new_width * new_height}")
        
        # 缩放图片
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)  # pyright: ignore[reportAttributeAccessIssue]
        logger.debug("图片缩放成功")
        
        return resized_image
    
    def get_pixel_data(self, image: Image.Image) -> list[list[tuple]]:
        """获取图片像素数据，返回二维数组，每个元素为RGBA元组"""
        width, height = image.size
        logger.info(f"获取图片像素数据，尺寸: {width}x{height}")
        
        pixel_data = []
        for y in range(height):
            row = []
            for x in range(width):
                pixel = image.getpixel((x, y))
                row.append(pixel)
            pixel_data.append(row)
        
        logger.debug(f"像素数据获取成功，共 {len(pixel_data)} 行，每行 {len(pixel_data[0])} 个像素")
        return pixel_data
    
    def rgba_to_hex(self, rgba: tuple) -> str:
        """将RGBA元组转换为16进制字符串，不带#号"""
        r, g, b, a = rgba
        # ADOFAI使用的是RGB，忽略Alpha通道
        return f"{r:02x}{g:02x}{b:02x}"
    
    def process_image(self, file_path: str, max_pixels: int) -> tuple[list[list[tuple]], int, int]:
        """完整处理流程：加载、缩放、获取像素数据"""
        logger.info(f"开始处理图片: {file_path}")
        logger.info(f"最大像素数限制: {max_pixels}")
        
        # 加载图片
        image = self.load_image(file_path)
        
        # 缩放图片
        resized_image = self.resize_image(image, max_pixels)
        
        # 获取像素数据
        pixel_data = self.get_pixel_data(resized_image)
        
        width, height = resized_image.size
        logger.info(f"图片处理完成，最终尺寸: {width}x{height}")
        
        return pixel_data, width, height
