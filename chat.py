from flask import Flask, request, jsonify, send_from_directory
import os
import openai
from dotenv import load_dotenv
from gtts import gTTS
import time

load_dotenv()

app = Flask(__name__)

client = openai.Client(api_key="sk-proj--dwUytJZQGU1g74DXxUrLXlESmHbWZEQXf0If1bAp01H5afpIey9aNOoYho-bQETslzC6dKwgsT3BlbkFJAbD2pqD_MMomqSJHIFO4inpI789Qd8mz8ocl3pGrAQDN2GdFum8VL95qxzB8gkcRQZzWFA")
global filename

@app.route('/')
def index():
    return send_from_directory('.', 'signals.html')

@app.route('/api/data', methods=['POST'])
def upload():
    # The 'request' object is now used correctly here, inside a route function.
    print("post successful")
    stress_level = request.args.get('stress_level', '')
    file = interpret(stress_level)
    filename = file
    return jsonify({"status": "post successful"}), 200

@app.route('/api/data', methods=['GET'])
def download():
    return jsonify({'': filename}), 200

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
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    filename = f"tts_{int(time.time())}.wav"
    filepath = os.path.join(output_folder, filename)

    try:
        tts = gTTS(text=text, lang='en')
        tts.save(filepath)
        return f"{filename}"
    except Exception as e:
        print(f"Error during TTS generation: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
