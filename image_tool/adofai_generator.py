# ADOFai关卡生成模块
from common.Logger import get_logger
logger = get_logger("关卡生成")

import json
from image_tool.image_processor import ImageProcessor

class ADOFAIGenerator:
    def __init__(self, pixel_data: list[list[tuple]], width: int, height: int):
        """初始化ADOFai生成器"""
        self.pixel_data = pixel_data
        self.width = width
        self.height = height
        self.image_processor = ImageProcessor()
        self.angleData = []
        self.actions = []
        self.level_data = {}

        self.actions.append(
            {
        "floor":0,
        "eventType":"MoveTrack",
        "startTile":[0,"Start"],
        "endTile":[0,"End"],
        "gapLength":0,
        "duration":0,
        "scale":[100,179.6407],
        "angleOffset":0,
        "ease":"Linear",
        "maxVfxOnly":False,
        "eventTag":""
        }
        )
    
    def generate_angle_data(self):
        """生成angleData数组，同一行像素为0"""
        logger.info(f"生成angleData，总像素数: {self.width * self.height}")
        # 每个像素对应一个0
        self.angleData = [0] * (self.width * self.height)
        logger.debug(f"angleData生成完成，长度: {len(self.angleData)}")
    
    def generate_actions(self):
        """生成actions数组，包含ColorTrack和PositionTrack事件"""
        logger.info("开始生成actions数组")
        
        # 在第二个砖块添加MoveCamera事件
        # 计算zoom：5000对应300x300，按比例计算
        base_zoom = 5000
        base_size = 300
        # 取宽度和高度的最大值作为参考尺寸
        reference_size = max(self.width, self.height)
        self.zoom = int(base_zoom * (reference_size / base_size))
        
        # 计算position：x为横尺寸的0.5倍，y为纵尺寸的-0.5倍
        self.cmr_position_x = int(self.width * 0.5)
        self.cmr_position_y = int(self.height * -0.5)
        
        # 生成MoveCamera事件（floor=1表示第二个砖块）
        # move_camera_action = {
        #     "floor": 0,
        #     "eventType": "MoveCamera",
        #     "relativeTo": "Tile",
        #     "duration": 0,
        #     "position": [self.cmr_position_x, self.cmr_position_y],
        #     "zoom": zoom,
        #     "angleOffset": 0,
        #     "ease": "OutCubic",
        #     "eventTag": ""
        # }

        # self.actions.append(move_camera_action)
        # logger.info(f"生成MoveCamera事件，砖块: 1，zoom: {zoom}，position: [{self.cmr_position_x}, {self.cmr_position_y}]")
        
        floor = 1
        last_color = None
        
        for y in range(self.height):
            for x in range(self.width):
                pixel = self.pixel_data[y][x]
                hex_color = self.image_processor.rgba_to_hex(pixel)
                
                # 只有当前颜色与上一个不同时，才生成ColorTrack事件
                if hex_color != last_color:
                    # 生成ColorTrack事件
                    color_action = {
                        "floor": floor,
                        "eventType": "ColorTrack",
                        "trackColorType": "Single",
                        "trackColor": hex_color,
                        "secondaryTrackColor": "ffffff",
                        "trackColorAnimDuration": 0,
                        "trackColorPulse": "None",
                        "trackPulseLength": 10,
                        "trackStyle": "Minimal",
                        "trackTexture": "",
                        "trackTextureScale": 1,
                        "trackGlowIntensity": 100,
                        "justThisTile": False
                    }
                    self.actions.append(color_action)
                    logger.debug(f"生成ColorTrack事件，砖块: {floor}，颜色: {hex_color}")
                    # 更新上一个颜色
                    last_color = hex_color
                else:
                    logger.debug(f"跳过ColorTrack事件，砖块: {floor}，颜色与上一个相同: {hex_color}")
                
                floor += 1
            
            # 每行结束后生成PositionTrack事件，用于换行
            # 最后一行不需要换行
            if y < self.height - 1:
                # 后续生成PositionTrack事件，使用原始偏移量
                x_offset = -self.width
                logger.debug(f"后续生成PositionTrack事件，使用原始偏移量: [{x_offset}, -1]")
                
                position_action = {
                    "floor": floor,
                    "eventType": "PositionTrack",
                    "positionOffset": [x_offset, -1],
                    "relativeTo": [0, "ThisTile"],
                    "justThisTile": False,
                    "editorOnly": False
                }
                self.actions.append(position_action)
                logger.debug(f"生成PositionTrack事件，砖块: {floor}，偏移量: [{x_offset}, -1]")
    
    def generate_level(self):
        """生成完整的关卡数据"""
        logger.info("开始生成完整关卡数据")
        
        # 生成angleData
        self.generate_angle_data()
        
        # 生成actions
        self.generate_actions()
        
        # 基础关卡数据结构
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
                "bpm": 100,
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
                "position": [self.cmr_position_x, self.cmr_position_y],
                "rotation": 0,
                "zoom": self.zoom,
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
        logger.debug(f"总砖块数: {len(self.angleData)}")
        logger.debug(f"总事件数: {len(self.actions)}")
    
    def save_level(self, file_path: str):
        """保存关卡到文件"""
        logger.info(f"保存关卡到文件: {file_path}")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.level_data, f, indent=2, ensure_ascii=False)
            logger.info("关卡保存成功")
        except Exception as e:
            logger.error(f"关卡保存失败: {e}")
            raise
    
    def generate_and_save(self, output_path: str):
        """生成并保存关卡"""
        self.generate_level()
        self.save_level(output_path)
