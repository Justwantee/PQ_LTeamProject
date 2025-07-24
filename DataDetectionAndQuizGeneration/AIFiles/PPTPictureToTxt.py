import easyocr
def process(file_path):
    """
        使用 EasyOCR 识别图片中的文字。
        参数:
            image_path: 图片文件路径。
            lang: 语言代码，默认为简体中文（'ch_sim'）。
        返回:
            识别出的文字列表。
        """
    # 创建 EasyOCR Reader，指定语言为简体中文
    reader = easyocr.Reader(['ch_sim'])
    # 读取图片并识别文字
    results = reader.readtext(file_path)
    if results:
        print("识别出的文字：")
        for (bbox, text, prob) in results:
            print(f"文本: {text}, 置信度: {prob}")
            with open("txt_QuizSource/ppt_text.txt", "a", encoding="utf-8") as f:
                f.write(text)
    else:
        print("未识别到文字")
    generated = []
    generated.append('txt_QuizSource/ppt_text.txt')
    return generated


def ocr_image(image_path, lang='ch_sim'):
    """
    使用 EasyOCR 识别图片中的文字。
    参数:
        image_path: 图片文件路径。
        lang: 语言代码，默认为简体中文（'ch_sim'）。
    返回:
        识别出的文字列表。
    """
    # 创建 EasyOCR Reader，指定语言为简体中文
    reader = easyocr.Reader([lang])
    # 读取图片并识别文字
    results = reader.readtext(image_path)
    return results

# 示例用法
image_path = ""  # 替换为你的图片路径
recognized_text = ocr_image(image_path, lang='ch_sim')  # 使用简体中文模型

if recognized_text:
    print("识别出的文字：")
    for (bbox, text, prob) in recognized_text:
        print(f"文本: {text}, 置信度: {prob}")
else:
    print("未识别到文字")
