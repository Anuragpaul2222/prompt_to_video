import sys
sys.path.append(r"C:\Users\KIIT01\AppData\Local\Programs\Python\Python311\Lib\site-packages")

import openai
from gtts import gTTS
from moviepy.editor import (
    ImageClip,
    concatenate_videoclips,
    AudioFileClip,
    CompositeVideoClip
)


from dotenv import load_dotenv

import os
import re
import textwrap

# === Load environment variables ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === Get user prompt ===
user_prompt = input("Enter your video prompt: ")

# === Generate script using OpenAI ===
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": user_prompt}],
    max_tokens=300
)

script = response['choices'][0]['message']['content'].strip()
print("\nGenerated Script:\n", script)

# === Convert script to speech ===
tts = gTTS(text=script)
voice_path = "output/voice.mp3"
tts.save(voice_path)
audio = AudioFileClip(voice_path)
duration = audio.duration

# === Split script into sentences ===
sentences = re.split(r'(?<=[.!?]) +', script)
time_per_sentence = duration / len(sentences)

# === Create subtitle clips ===
subtitle_clips = []
start_time = 0

for sentence in sentences:
    wrapped = "\n".join(textwrap.wrap(sentence, width=60))
    txt_clip = (
        TextClip(wrapped, fontsize=42, color='white', bg_color='black', size=(1280, 720), method='caption')
        .set_position('center')
        .set_duration(time_per_sentence)
        .set_start(start_time)
    )
    subtitle_clips.append(txt_clip)
    start_time += time_per_sentence

# === Optional: background video or fallback to black background ===
bg_path = "assets/bg.mp4"
if os.path.exists(bg_path):
    background = VideoFileClip(bg_path).subclip(0, duration).resize((1280, 720))
else:
    background = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=duration)

# === Compose final video ===
final_video = CompositeVideoClip([background] + subtitle_clips).set_audio(audio)

# === Export ===
output_path = "output/generated_video.mp4"
final_video.write_videofile(output_path, fps=24)

print(f"\n✅ Video created successfully: {output_path}")

