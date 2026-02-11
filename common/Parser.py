# 解析模块
from Logger import get_logger
logger = get_logger("解析")

import json
import re

class Parser:
    def __init__(self, file_path: str) -> None:
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            self.content: str = file.read()
        
        self.Data: dict = self.parse(self.content)
        if "pathData" in self.Data:
            self.convert_pathData_to_angleData()
    
    def __call__(self) -> dict:
        return self.Data
    
    def repair_json(self, text: str) -> dict:
        json_text: str = ''.join(ch for ch in text if ch.isprintable())
        if json_text.startswith('\ufeff'):
            json_text = json_text[1:]
        
        try:
            data = json.loads(json_text)
            return data
        except json.JSONDecodeError as e:
            pass
        
        # 常见修复步骤
        repaired: str = json_text
        
        # 移除 ] 或 } 前多余的逗号
        repaired = re.sub(r',\s*([}\]])', r'\1', repaired)
        
        # 如有需要，补全缺失的右括号
        open_braces: int = repaired.count('{') - repaired.count('}')
        open_brackets: int = repaired.count('[') - repaired.count(']')
        
        if open_braces > 0:
            repaired += '}' * open_braces
        if open_brackets > 0:
            repaired += ']' * open_brackets
        
        # 修复被截断的文件，补全所有未闭合的结构
        # 统计所有未闭合的结构并补全
        stack: list[tuple[str, int]] = []
        for i, char in enumerate(repaired):
            if char == '{':
                stack.append(('}', i))
            elif char == '[':
                stack.append((']', i))
            elif char == '}' or char == ']':
                if stack and stack[-1][0] == char:
                    stack.pop()
        
        # 按逆序补全缺失的右括号
        for char, _ in reversed(stack):
            repaired += char
        
        try:
            data = json.loads(repaired)
            return data
        except json.JSONDecodeError as e:
            pass

        repaired = json_text.replace('\n', '') \
                .replace(" ", "") \
                .replace("	", "") \
                .replace(',,', ',') \
                .replace(',]', ']') \
                .replace(',}', '}') \
                .replace(']"', '],"')

        try:
            data: dict = json.loads(repaired)
            return data

        except json.JSONDecodeError as e:
            logger.error(f"修复JSON失败: {e}")
            return {}
    
    def parse(self, data: str) -> dict:
        return self.repair_json(data)

    def convert_pathData_to_angleData(self) -> None:
        """将路径数据转换为角度数据"""
        angleData: list = []
        for c in self.Data["pathData"]:
            if c == 'R': angleData.append(0)
            elif c == 'L': angleData.append(180)
            elif c == 'U': angleData.append(90)
            elif c == 'D': angleData.append(-90)
            elif c == 'E': angleData.append(45)
            elif c == 'Q': angleData.append(135)
            elif c == 'Z': angleData.append(-135)
            elif c == 'C': angleData.append(-45)
            elif c == 'J': angleData.append(30)
            elif c == 'T': angleData.append(60)
            elif c == 'G': angleData.append(120)
            elif c == 'H': angleData.append(150)
            elif c == 'N': angleData.append(-150)
            elif c == 'F': angleData.append(-120)
            elif c == 'B': angleData.append(-60)
            elif c == 'M': angleData.append(-30)
            elif c == 'p': angleData.append(15)
            elif c == 'A': angleData.append(-15)
            elif c == 'Y': angleData.append(-75)
            elif c == 'V': angleData.append(-105)
            elif c == 'x': angleData.append(-165)
            elif c == 'W': angleData.append(165)
            elif c == 'q': angleData.append(105)
            elif c == 'o': angleData.append(75)
            elif c == '!': angleData.append(999)
            elif c == '5': angleData.append(angleData[-1] + 72)
            elif c == '6': angleData.append(angleData[-1] - 72)
            elif c == '7': angleData.append(angleData[-1] + 360/7)
            elif c == '8': angleData.append(angleData[-1] - 360/7)
            else:
                logger.error(f"未知操作符: {c}")
                raise ValueError(f"未知操作符: {c}")
        self.Data["angleData"] = angleData
