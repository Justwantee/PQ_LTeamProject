import os
import importlib
import logging
import glob
import re
from collections import defaultdict, deque
from openai import OpenAI

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 文件类型与处理模块的映射
PROCESSOR_MAPPING = {
    # 视频文件
    '.mp4': 'videoPPTDetect',
    '.avi': 'videoPPTDetect',
    '.mov': 'videoPPTDetect',
    '.mkv': 'videoPPTDetect',

    # PDF文件
    '.pdf': 'pdfToTxt',

    # 图像文件
    '.jpg': 'PPTPictureToTxt',
    '.jpeg': 'PPTPictureToTxt',
    '.png': 'PPTPictureToTxt',

    # 文本文件
    '.txt': 'txtToTxt',
    '.doc': 'txtToTxt',
    '.docx': 'txtToTxt',
    '.ppt': 'txtToTxt',
    '.pptx': 'txtToTxt',
    '.xls': 'txtToTxt',
    '.xlsx': 'txtToTxt',

    # 音频文件
    '.wav': 'voiceFileToTxt',
}

# OpenAI客户端配置
OPENAI_CLIENT = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)


def get_file_processor(file_path):
    """获取文件对应的处理模块"""
    ext = os.path.splitext(file_path)[1].lower()
    module_name = PROCESSOR_MAPPING.get(ext)
    if not module_name:
        return None

    try:
        return importlib.import_module(module_name)
    except ImportError:
        logging.error(f"处理模块 {module_name} 未找到 (文件: {file_path})")
    except Exception as e:
        logging.error(f"导入模块 {module_name} 时出错: {str(e)}")
    return None


def process_directory(directory):
    """处理目录中的所有文件"""
    # 使用队列管理待处理文件（包括新生成的）
    file_queue = deque()
    processed_files = set()
    unsupported_files = []

    # 初始扫描目录
    for filename in sorted(os.listdir(directory)):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            if get_file_processor(filename):
                file_queue.append(file_path)
            else:
                unsupported_files.append(filename)

    # 记录不支持的文件
    if unsupported_files:
        logging.warning(f"跳过 {len(unsupported_files)} 个不支持的文件: {', '.join(unsupported_files)}")

    # 处理队列中的文件
    while file_queue:
        file_path = file_queue.popleft()

        # 跳过已处理文件
        if file_path in processed_files:
            continue

        processed_files.add(file_path)
        filename = os.path.basename(file_path)

        processor_module = get_file_processor(filename)
        if not processor_module:
            continue

        try:
            logging.info(f"处理: {filename}")

            # 调用处理模块并获取生成的新文件列表
            new_files = processor_module.process(file_path)

            # 将新生成的文件添加到队列
            if new_files:
                logging.info(f"添加 {len(new_files)} 个新生成文件到处理队列")
                for new_file in new_files:
                    if os.path.isfile(new_file) and new_file not in processed_files:
                        file_queue.append(new_file)

        except Exception as e:
            logging.error(f"处理文件 {file_path} 失败: {str(e)}")

    return processed_files


def generate_quiz_from_texts():
    """从txt_QuizSource目录中的txt文件生成选择题"""
    quiz_source_dir = "txt_QuizSource"
    quiz_output_file = "Quiz/generated_quiz.txt"

    # 确保目录存在
    if not os.path.exists(quiz_source_dir):
        os.makedirs(quiz_source_dir)
        logging.info(f"创建目录: {quiz_source_dir}")
        return

    # 收集所有txt文件内容
    txt_files = glob.glob(os.path.join(quiz_source_dir, "*.txt"))
    if not txt_files:
        logging.warning(f"{quiz_source_dir} 目录中没有找到txt文件")
        return

    combined_content = ""
    for file_path in txt_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    combined_content += f"### 文本片段:\n{content}\n\n"
        except Exception as e:
            logging.error(f"读取文件 {file_path} 失败: {str(e)}")

    if not combined_content:
        logging.warning(f"{quiz_source_dir} 目录中的txt文件均为空")
        return

    # 生成提示词
    prompt = (
        "你是一位大学老师，需要根据以下的内容为大学四年级学生设计多道高质量的选择题。\n"
        "要求：\n"
        "1. 题目难度适中，符合大四学生认知水平\n"
        "2. 每道题有4个选项，只有1个正确答案\n"
        "3. 题目应覆盖文本中的关键知识点\n"
        "4. 题目格式：'问题\nA. 选项A\nB. 选项B\nC. 选项C\nD. 选项D\n答案: [选项字母]'\n\n"
        "文本内容:\n"
        f"{combined_content}"
    )

    logging.info("开始生成选择题...")

    try:
        # 调用OpenAI API生成题目
        completion = OPENAI_CLIENT.chat.completions.create(
            model="deepseek/deepseek-r1-0528:free",
            messages=[
                {"role": "system", "content": "你是一位经验丰富的大学老师，擅长根据文本内容设计高质量的选择题"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )

        quiz_content = completion.choices[0].message.content

        # 保存生成的题目
        with open(quiz_output_file, 'w', encoding='utf-8') as f:
            f.write("")
        with open(quiz_output_file, 'a', encoding='utf-8') as f:
            f.write(quiz_content)
        logging.info(f"已生成选择题并保存到: {quiz_output_file}")

        # 清空txt_QuizSource目录中的文件
        for file_path in txt_files:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("")  # 清空文件内容
            except Exception as e:
                logging.error(f"清空文件 {file_path} 失败: {str(e)}")
        logging.info(f"已清空 {quiz_source_dir} 目录中的文件内容")

    except Exception as e:
        logging.error(f"生成选择题失败: {str(e)}")


def clean_directory(directory):
    """清理目录中的空文件和临时文件"""
    logging.info(f"清理目录: {directory}")
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            try:
                # 删除空文件
                if os.path.getsize(file_path) == 0:
                    os.remove(file_path)
                    logging.info(f"删除空文件: {filename}")
                # 删除临时文件（示例，根据实际需求调整）
                elif filename.endswith('.tmp') or filename.startswith('~'):
                    os.remove(file_path)
                    logging.info(f"删除临时文件: {filename}")
            except Exception as e:
                logging.error(f"处理文件 {filename} 失败: {str(e)}")


if __name__ == "__main__":
    # 配置要处理的文件夹路径
    TARGET_DIRECTORY = "inputFiles"
    QUIZ_SOURCE_DIR = "txt_QuizSource"

    if not os.path.exists(TARGET_DIRECTORY):
        logging.error(f"目标文件夹不存在: {TARGET_DIRECTORY}")
    else:
        logging.info(f"开始处理目录: {TARGET_DIRECTORY}")
        processed_files = process_directory(TARGET_DIRECTORY)
        logging.info(f"所有文件处理完成，共处理 {len(processed_files)} 个文件")

        # 生成选择题
        generate_quiz_from_texts()

        # 清理inputFiles目录
        clean_directory(TARGET_DIRECTORY)
        logging.info("程序执行完毕")