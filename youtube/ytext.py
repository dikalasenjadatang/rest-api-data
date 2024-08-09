import yt_dlp
import speech_recognition as sr
from pydub import AudioSegment
from deep_translator import GoogleTranslator
import math

# Specify the path to FFmpeg executable
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"  # Update this path

# URL video YouTube
video_url = 'https://www.youtube.com/watch?v=In5aLKsMPJc'

# Unduh video menggunakan yt-dlp
def download_video(url, output_format='mp4'):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'video.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'ffmpeg_location': FFMPEG_PATH,  # Add this line
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# Ubah file audio menjadi format yang didukung
def convert_audio(input_file, output_file):
    audio = AudioSegment.from_wav(input_file)
    audio.export(output_file, format='wav')

# Transkripsikan audio dan terjemahkan ke Bahasa Indonesia
def transcribe_and_translate_audio(file):
    recognizer = sr.Recognizer()
    translator = GoogleTranslator(source='id', target='id')
    full_transcript = []
    
    audio = AudioSegment.from_wav(file)
    chunk_length_ms = 30000  # 30 seconds
    chunks = math.ceil(len(audio) / chunk_length_ms)
    
    for i in range(chunks):
        start_time = i * chunk_length_ms
        end_time = (i + 1) * chunk_length_ms
        chunk = audio[start_time:end_time]
        
        with sr.AudioFile(chunk.export(format="wav")) as source:
            audio_chunk = recognizer.record(source)
        
        try:
            text = recognizer.recognize_google(audio_chunk, language='id-ID')
            translated = translator.translate(text)
            full_transcript.append((start_time / 1000, translated))
        except sr.UnknownValueError:
            full_transcript.append((start_time / 1000, "Audio tidak dapat dikenali"))
        except sr.RequestError:
            full_transcript.append((start_time / 1000, "Tidak dapat terhubung ke layanan Google"))
    
    return full_transcript

# Simpan teks transkripsi sebagai subtitle SRT
def save_srt(transcription, filename='subtitle.srt'):
    with open(filename, 'w', encoding='utf-8') as file:
        for i, (start_time, text) in enumerate(transcription, 1):
            end_time = transcription[i][0] if i < len(transcription) else start_time + 5
            start_time_fmt = format_time(int(start_time))
            end_time_fmt = format_time(int(end_time))
            file.write(f"{i}\n{start_time_fmt} --> {end_time_fmt}\n{text}\n\n")

def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},000"

# Main function
if __name__ == '__main__':
    download_video(video_url)
    convert_audio('video.wav', 'audio.wav')
    transcription = transcribe_and_translate_audio('audio.wav')
    save_srt(transcription)
    print("Transkripsi dan terjemahan selesai dan disimpan sebagai subtitle.srt")