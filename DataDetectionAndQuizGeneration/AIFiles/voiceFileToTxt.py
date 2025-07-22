from vosk import Model,KaldiRecognizer
import wave
import pyaudio
import json
def process(file_path):
 #音频文件识别
 voiceModel= Model('vosk-model-small-cn-0.22')
 voiceFile=wave.open(file_path, 'rb')
 voiceRecognizer=KaldiRecognizer(voiceModel,16000)
 while True:
     recognizeData=voiceFile.readframes(4000)
     if not recognizeData:
         break
     voiceRecognizer.AcceptWaveform(recognizeData)
     outputResult = voiceRecognizer.Result()
     txt_path = "txt_QuizSource/voice_text.txt"  # 根据需要修改路径
     with open(txt_path, "a", encoding="utf-8") as file:
         file.write(json.loads(outputResult)['text'].replace(' ',''))
 generated = []
 generated.append('txt_QuizSource/voice_text.txt')
 return generated
