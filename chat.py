from flask import Flask, request, jsonify, send_from_directory
import os
import openai
from dotenv import load_dotenv
from gtts import gTTS
import time

from pydub import AudioSegment

load_dotenv()

app = Flask(__name__)

client = openai.Client(api_key="sk-proj--dwUytJZQGU1g74DXxUrLXlESmHbWZEQXf0If1bAp01H5afpIey9aNOoYho-bQETslzC6dKwgsT3BlbkFJAbD2pqD_MMomqSJHIFO4inpI789Qd8mz8ocl3pGrAQDN2GdFum8VL95qxzB8gkcRQZzWFA")
filename=''
ready=False

@app.route('/')
def index():
    return send_from_directory('.', 'signals.html')

@app.route('/api/data', methods=['POST'])
def upload():
    # The 'request' object is now used correctly here, inside a route function.
    global filename
    print("post successful")
    stress_level = request.args.get('stress_level', '')
    filename = interpret(stress_level)
    print(filename)
    return jsonify({"status": "post successful"}), 200

@app.route('/api/data', methods=['GET'])
def download():
    global ready
    if ready:

        ready = False
        return jsonify({'file': str(filename)}), 200
    else:
        return jsonify({'file': 'Not ready'}), 200

def interpret(stress_level):
    prompt = f"""
        You are a health assistant specializing in mindfulness and stress reduction. Your task is to provide a short, tailored mindfulness meditation based on a user's self-reported stress level from 1-10.

        Based on the following stress level:
        Stress level: {stress_level}

        Follow these rules for your response:
        1.  For a stress level of 1-3 (Low Stress): Provide a simple, brief mindfulness exercise focused on awareness and appreciation of the present moment. The exercise should be light and encouraging.
        2.  For a stress level of 4-7 (Moderate Stress): Provide a more detailed and structured mindfulness exercise. Focus on deep breathing and body scanning to help the user ground themselves and release tension.
        3.  For a stress level of 8-10 (High Stress): Provide a very simple, direct, and grounding mindfulness exercise. The focus should be on calming the nervous system with very clear, step-by-step instructions for a short breathing technique. Avoid complex language.

        Your response should be a complete mindfulness meditation that the user can follow immediately.
    """

    try:

        #response = client.chat.completions.create(
        #    model="gpt-3.5-turbo",
        #    messages=[
        #        {"role": "system", "content": "You are an expert in physiology and emotional health."},
        #        {"role": "user", "content": prompt}
        #    ],
        #    max_tokens=150,
        #    temperature=0
        #)
        result = prompt#response.choices[0].message.content.strip()
        #print(result)
        file = text_to_wav_cli(result)
        return file
    except Exception as e:
        print(str(e))
        return str(e)

def text_to_wav_cli(text, output_folder="tts_output"):
    """
    Generates a WAV file from the given text using gTTS and converts it to a PCM WAV
    (16-bit, 16kHz, mono) format suitable for NVIDIA ACE.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    timestamp = int(time.time())
    mp3_filename = f"tts_{timestamp}.mp3"
    mp3_filepath = os.path.join(output_folder, mp3_filename)
    wav_filename = f"tts_{timestamp}.wav"
    wav_filepath = os.path.join(output_folder, wav_filename)

    try:
        # Generate TTS MP3
        tts = gTTS(text=text, lang='en')
        tts.save(mp3_filepath)

        # Convert to WAV with correct format
        sound = AudioSegment.from_mp3(mp3_filepath)
        sound = sound.set_frame_rate(16000).set_channels(1).set_sample_width(2)  # 16kHz, mono, 16-bit
        sound.export(wav_filepath, format="wav", codec="pcm_s16le")

        os.remove(mp3_filepath)  # Clean up MP3 file
        global ready
        ready = True
        return wav_filename
    except Exception as e:
        print(f"Error during TTS generation or conversion: {e}")
        return None


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
