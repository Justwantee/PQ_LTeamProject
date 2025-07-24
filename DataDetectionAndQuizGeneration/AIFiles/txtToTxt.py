import textract
import os
import chardet
import logging
import re
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("text_extraction.log"),
        logging.StreamHandler()
    ]
)


def extract_text_from_file(file_path):
    """
    从指定文件中提取文本内容，优化中文编码处理
    :param file_path: 文件路径
    :return: 提取的文本内容
    """
    try:
        # 获取文件扩展名
        ext = os.path.splitext(file_path)[1].lower()

        # 对于文本文件，使用更智能的编码检测
        if ext in ['.txt', '.md', '.csv', '.log']:
            # 先尝试用二进制读取文件内容
            with open(file_path, 'rb') as f:
                raw_data = f.read()

            # 检测文件编码
            encoding_detect = chardet.detect(raw_data)
            encoding = encoding_detect['encoding'] or 'utf-8'
            confidence = encoding_detect['confidence']

            # 如果检测置信度低，尝试常见中文编码
            if confidence < 0.7:
                for enc in ['utf-8', 'gbk', 'gb18030', 'big5']:
                    try:
                        text = raw_data.decode(enc, errors='strict')
                        logging.info(f"使用备用编码成功解码: {enc}")
                        return text
                    except:
                        continue

            # 尝试解码
            try:
                text = raw_data.decode(encoding, errors='strict')
            except:
                # 严格模式失败时使用忽略错误模式
                text = raw_data.decode(encoding, errors='ignore')

            return text

        # 对于其他文件类型使用textract
        raw_data = textract.process(file_path)

        # 检测文件编码
        encoding_detect = chardet.detect(raw_data)
        encoding = encoding_detect['encoding'] or 'utf-8'

        # 尝试解码（忽略无法解码的字符）
        return raw_data.decode(encoding, errors='ignore')

    except Exception as e:
        logging.error(f"提取文件 {file_path} 时发生错误：{e}")
        return ""


def clean_text(text):
    """清理和规范化文本内容"""
    # 移除无效字符
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    # 规范化换行符
    text = re.sub(r'\r\n', '\n', text)
    # 移除多余空行
    text = re.sub(r'\n{3,}', '\n\n', text)
    # 移除行首行尾空白
    text = '\n'.join(line.strip() for line in text.splitlines())
    return text.strip()


def process(file_path):
    """
    优化处理单个文件：提取文本并保存到单独文件
    :param file_path: 要处理的文件路径
    :return: 生成的文本文件路径列表
    """
    start_time = datetime.now()
    generated = []

    try:
        # 确保输出目录存在
        os.makedirs('txt_QuizSource', exist_ok=True)

        # 检查文件是否存在
        if not os.path.exists(file_path):
            logging.error(f"文件不存在: {file_path}")
            return generated

        filename = os.path.basename(file_path)
        logging.info(f"开始处理文件: {filename}")

        # 提取文件文本
        text = extract_text_from_file(file_path)

        if not text.strip():
            logging.warning("提取到的文本内容为空")
            return generated

        # 清理文本
        cleaned_text = clean_text(text)

        # 创建单独的输出文件（每个原始文件对应一个txt文件）
        output_filename = f"{os.path.splitext(filename)[0]}.txt"
        output_path = os.path.join('txt_QuizSource', output_filename)

        # 写入输出文件
        with open(output_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(cleaned_text)

        processing_time = datetime.now() - start_time
        logging.info(f"文件处理成功: {filename} -> {output_filename}")
        logging.info(f"处理用时: {processing_time.total_seconds():.2f}秒")
        logging.info(f"提取字符数: {len(cleaned_text)}")

        generated.append(output_path)
        return generated

    except Exception as e:
        logging.error(f"处理文件 {file_path} 时发生错误: {e}")
        return generated


