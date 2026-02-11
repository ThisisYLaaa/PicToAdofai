# 视频转ADOFai模块
from common.Logger import get_logger
logger = get_logger("视频转ADOFai")

from typing import Optional
import json
from image_tool.image_processor import ImageProcessor

class VideoToADOFai:
    def __init__(self):
        """初始化视频转ADOFai转换器"""
        self.image_processor = ImageProcessor()
        self.angleData = []
        self.actions = []
        self.level_data = {}
    
    def generate_angle_data(self, width: int, height: int) -> list[int]:
        """生成angleData数组"""
        logger.info(f"生成angleData，总像素数: {width * height}")
        # 每个像素对应一个0
        angleData = [0] * (width * height)
        logger.debug(f"angleData生成完成，长度: {len(angleData)}")
        return angleData
    
    def generate_recolortrack_events(self, frame_index: int, pixel_data: list[list[tuple]], width: int, height: int, fps: float, diff_threshold: float = 10.0, prev_frame_data: Optional[list[list[tuple]]] = None) -> list[dict]:
        """生成Recolortrack事件"""
        
        events = []
        floor = 1  # 轨道索引从1开始
        
        # 计算当前帧的angleOffset
        angle_offset = frame_index * (180 / fps)
        logger.debug(f"第 {frame_index+1} 帧的angleOffset: {angle_offset:.2f}")
        
        for y in range(height):
            for x in range(width):
                pixel = pixel_data[y][x]
                hex_color = self.image_processor.rgba_to_hex(pixel)
                
                # 检查与前一帧的差异
                if prev_frame_data is not None:
                    prev_pixel = prev_frame_data[y][x]
                    prev_hex_color = self.image_processor.rgba_to_hex(prev_pixel)
                    
                    # 计算颜色差异
                    r1, g1, b1, _ = pixel
                    r2, g2, b2, _ = prev_pixel
                    color_diff = ((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2)**0.5
                    
                    # 如果差异小于阈值，跳过
                    if color_diff < diff_threshold:
                        logger.debug(f"跳过轨道 {floor}，颜色差异较小: {color_diff:.2f}")
                        floor += 1
                        continue
                
                # 生成Recolortrack事件
                recolortrack_event = {
                    "floor": 1,
                    "eventType": "RecolorTrack",
                    "startTile": [floor, "Start"],
                    "endTile": [floor, "Start"],
                    "gapLength": 0,
                    "duration": 0,
                    "trackColorType": "Single",
                    "trackColor": hex_color,
                    "secondaryTrackColor": "ffffffff",
                    "trackColorAnimDuration": 2,
                    "trackColorPulse": "None",
                    "trackPulseLength": 10,
                    "trackStyle": "Minimal",
                    "trackGlowIntensity": 100,
                    "eventTag": "",
                    "angleOffset": angle_offset
                }
                
                events.append(recolortrack_event)
                logger.debug(f"生成Recolortrack事件，轨道: {floor}，颜色: {hex_color}，angleOffset: {angle_offset:.2f}")
                
                floor += 1
        
        logger.info(f"第 {frame_index+1} 帧生成完成，共 {len(events)} 个Recolortrack事件")
        return events
    
    def generate_level(self, frames: list[tuple[list[list[tuple]], int, int]], fps: float, diff_threshold: float = 10.0) -> dict:
        """生成完整的关卡数据"""
        logger.info(f"开始生成完整关卡数据，共 {len(frames)} 帧")
        
        try:
            # 获取第一帧的尺寸
            first_frame_data, width, height = frames[0]
            logger.info(f"使用第一帧的尺寸: {width}x{height}")
            
            # 生成angleData
            self.angleData = self.generate_angle_data(width, height)
            
            # 初始化actions数组
            self.actions = []
            
            # 在第一个砖块添加MoveTrack事件
            self.actions.append({
                "floor": 0,
                "eventType": "MoveTrack",
                "startTile": [0, "Start"],
                "endTile": [0, "End"],
                "gapLength": 0,
                "duration": 0,
                "scale": [100, 179.6407],
                "angleOffset": 0,
                "ease": "Linear",
                "maxVfxOnly": False,
                "eventTag": ""
            })
            
            # 计算相机设置
            base_zoom = 5000
            base_size = 300
            reference_size = max(width, height)
            zoom = int(base_zoom * (reference_size / base_size))
            cmr_position_x = int(width * 0.5)
            cmr_position_y = int(height * -0.5)
            
            logger.info(f"相机设置: zoom={zoom}, position=({cmr_position_x}, {cmr_position_y})")
            
            # 处理每一帧
            length = 0
            prev_frame_data = None
            for i, (frame_data, frame_width, frame_height) in enumerate(frames):
                # 确保所有帧尺寸相同
                if frame_width != width or frame_height != height:
                    logger.warning(f"第 {i+1} 帧尺寸与第一帧不同，跳过")
                    continue
                
                # 生成当前帧的Recolortrack事件
                frame_events = self.generate_recolortrack_events(
                    i, frame_data, width, height, fps, diff_threshold, prev_frame_data
                )
                
                # 添加到actions数组
                self.actions.extend(frame_events)
                
                # 更新前一帧数据
                prev_frame_data = frame_data
                
                # 更新长度
                length += len(frame_events)
            
            # 生成PositionTrack事件，用于换行
            logger.info("开始生成PositionTrack事件，用于轨道换行")
            floor = 1
            for y in range(height):
                floor += width  # 移动到当前行的末尾
                
                # 最后一行不需要换行
                if y < height - 1:
                    # 生成PositionTrack事件
                    position_action = {
                        "floor": floor,
                        "eventType": "PositionTrack",
                        "positionOffset": [-width, -1],
                        "relativeTo": [0, "ThisTile"],
                        "justThisTile": False,
                        "editorOnly": False
                    }
                    self.actions.append(position_action)
                    logger.debug(f"生成PositionTrack事件，砖块: {floor}，偏移量: [-{width}, -1]")
            
            logger.info(f"PositionTrack事件生成完成，共生成 {height-1 if height > 0 else 0} 个事件")
            
            # 生成基础关卡数据结构
            self.level_data = {
                "angleData": self.angleData,
                "settings": {
                    "version": 15,
                    "artist": "",
                    "specialArtistType": "None",
                    "artistPermission": "",
                    "song": "",
                    "author": "",
                    "separateCountdownTime": True,
                    "previewImage": "",
                    "previewIcon": "",
                    "previewIconColor": "003f52",
                    "previewSongStart": 0,
                    "previewSongDuration": 10,
                    "seizureWarning": False,
                    "levelDesc": "",
                    "levelTags": "",
                    "artistLinks": "",
                    "speedTrialAim": 0,
                    "difficulty": 1,
                    "requiredMods": [],
                    "songFilename": "",
                    "bpm": 60,  # 设置BPM为60
                    "volume": 100,
                    "offset": 0,
                    "pitch": 100,
                    "hitsound": "Kick",
                    "hitsoundVolume": 100,
                    "countdownTicks": 4,
                    "songURL": "",
                    "tileShape": "Long",
                    "trackColorType": "Single",
                    "trackColor": "debb7b",
                    "secondaryTrackColor": "ffffff",
                    "trackColorAnimDuration": 2,
                    "trackColorPulse": "None",
                    "trackPulseLength": 10,
                    "trackStyle": "Standard",
                    "trackTexture": "",
                    "trackTextureScale": 1,
                    "trackGlowIntensity": 100,
                    "trackAnimation": "None",
                    "beatsAhead": 3,
                    "trackDisappearAnimation": "None",
                    "beatsBehind": 4,
                    "backgroundColor": "000000",
                    "showDefaultBGIfNoImage": True,
                    "showDefaultBGTile": True,
                    "defaultBGTileColor": "101121",
                    "defaultBGShapeType": "Default",
                    "defaultBGShapeColor": "ffffff",
                    "bgImage": "",
                    "bgImageColor": "ffffff",
                    "parallax": [100, 100],
                    "bgDisplayMode": "FitToScreen",
                    "imageSmoothing": True,
                    "lockRot": False,
                    "loopBG": False,
                    "scalingRatio": 100,
                    "relativeTo": "Tile",
                    "position": [cmr_position_x, cmr_position_y],
                    "rotation": 0,
                    "zoom": zoom,
                    "pulseOnFloor": True,
                    "startCamLowVFX": False,
                    "bgVideo": "",
                    "loopVideo": False,
                    "vidOffset": 0,
                    "floorIconOutlines": False,
                    "stickToFloors": True,
                    "planetEase": "Linear",
                    "planetEaseParts": 1,
                    "planetEasePartBehavior": "Mirror",
                    "customClass": "",
                    "defaultTextColor": "ffffff",
                    "defaultTextShadowColor": "00000050",
                    "congratsText": "",
                    "perfectText": "",
                    "legacyFlash": False,
                    "legacyCamRelativeTo": False,
                    "legacySpriteTiles": False,
                    "legacyTween": False,
                    "disableV15Features": False
                },
                "actions": self.actions,
                "decorations": []
            }
            
            logger.info("关卡数据生成完成")
            logger.info(f"总砖块数: {len(self.angleData)}")
            logger.info(f"总事件数: {len(self.actions)}")
            logger.info(f"总recolortrack事件数量: {length}")

            return self.level_data
        except Exception as e:
            logger.error(f"生成关卡数据失败: {e}")
            raise
    
    def save_level(self, level_data: dict, file_path: str):
        """保存关卡到文件"""
        logger.info(f"保存关卡到文件: {file_path}")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(level_data, f, indent=2, ensure_ascii=False)
            logger.info("关卡保存成功")
        except Exception as e:
            logger.error(f"关卡保存失败: {e}")
            raise
    
    def convert(self, frames: list[tuple[list[list[tuple]], int, int]], fps: float, output_path: str, diff_threshold: float = 10.0):
        """执行转换过程"""
        logger.info("开始执行视频到ADOFai的转换")
        
        try:
            # 生成关卡数据
            level_data = self.generate_level(frames, fps, diff_threshold)
            
            # 保存关卡文件
            self.save_level(level_data, output_path)
            
            logger.info("转换完成！")
            return True
        except Exception as e:
            logger.error(f"转换失败: {e}")
            raise