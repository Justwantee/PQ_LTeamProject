import PyPDF2
def process(file_path):
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        with open('txt_QuizSource/pdf_text.txt', 'a', encoding='utf-8') as txt_file:
            txt_file.write(text)
        print(f"文字提取完成，已保存到 pdf_text.txt")
        generated = []
        generated.append('txt_QuizSource/pdf_text.txt')
        return generated
