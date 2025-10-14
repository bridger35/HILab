from flask import Flask, request, jsonify, send_from_directory
import os
import openai
import dotenv
from gtts import gTTS
import time

from pydub import AudioSegment

dotenv.load_dotenv()

app = Flask(__name__)

key = os.getenv("OPEN_API_KEY") #Dotenv file not stored on github becuase repo is public

client = openai.Client(api_key=key)
filename=''
ready=False

@app.route('/')
def index():
    return send_from_directory('.', 'signals.html')

@app.route('/api/data', methods=['POST'])
def upload():
    """
    :return: Turbosatori_Connection.py passes on stress level
    WAV file else pass not ready
    """
    global filename

    stress_level = request.json.get('stress_level')

    filename = main(stress_level)

    return jsonify({"status": "post successful"}), 200

@app.route('/api/data', methods=['GET'])
def download():
    """
    If the WAV file is generated then pass the filename to Unreal
    :return:
    """
    global ready
    if ready:

        ready = False
        return jsonify({'file': str(filename)}), 200
    else:
        return jsonify({'file': 'Not ready'}), 200

def chatGPT(stress_level):
    """
    :param stress_level:  1-10 value generated from Turbosatori analysis
    :return: Custom response as a health assitant aiming to calm a <stress_level> participant
    """
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
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in physiology and emotional health."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0
        )
        result = response.choices[0].message.content.strip()
        return result
    except Exception as e:
        print(e)
        return e




def text_to_wav_cli(text, output_folder="tts_output"):
    """
    Generates a MP3 file from the given text using gTTS and converts it to a PCM WAV
    using ffmpeg (16-bit, 16kHz, mono) format suitable for NVIDIA ACE.
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

def main(stress_level):
    """
    Use responses[] for hardcoded replies otherwise use chatGPT(<stress_level>)
    Passes stress level to chatGPT for custom response based on prompt
    Response is then passed to text_to_wav_cli for WAV file generation
    :param stress_level: 1-10 value generated from Turbosatori analysis
    :return: WAV filename
    """

    responses = [
        # Stress Level 1-3 (Low Stress)
        "Take a moment to notice a sound you might not have heard before. Listen to it for three full breaths, simply observing its quality without judgment.",
        "Breathe in a deep breath and as you do, feel the air as it moves into your lungs and fill your stomach. As you do, think of one thing you are grateful for today and sit in that for 15 seconds.",
        "As you take a drink of water, focus on the sensation of the cold glass in your hand and the feeling of the water moving down your throat. Notice every detail.",

        # Stress Level 4-7 (Moderate Stress)
        "Begin by taking a deep breath in through your nose, counting to four. Hold for four counts, then slowly exhale through your mouth for six. As you breathe, mentally scan your body, noticing any areas of tension and consciously softening them. Repeat this five times.",
        "Sit comfortably with your feet on the floor. Close your eyes and take a slow, deep breath. Focus on your breathing. Now, bring your awareness to your feet. Wiggle your toes. Slowly move your awareness up through your body, noticing any sensations in your legs, torso, and arms. Feel yourself grounded in this moment.",
        "Place one hand on your chest and the other on your stomach. Take a deep breath through your nose, feeling your stomach expand. Exhale slowly through your mouth. Pay attention to the rhythm of your breath and the rise and fall of your hands. Continue until you feel a sense of calm.",
        "Take a long, slow breath in through your nose, filling your lungs completely. Hold for a moment, then release a long, slow exhale through your mouth. As you exhale, imagine any tension or worry leaving your body. Repeat five times.",

        # Stress Level 8-10 (High Stress)
        "Take a slow, deep breath in for four counts. Hold for four counts. Exhale slowly for four counts. Repeat this three times. The only focus is the numbers and your breath.",
        "Sit down and close your eyes. Place your attention on your feet. Feel them grounded to the floor. Notice the pressure and the connection. As you exhale, imagine the tension leaving your body through your feet.",
        "Focus on your breath. Inhale: 1-2-3-4. Exhale: 1-2-3-4. Repeat this simple count for a few cycles. Your only job is to breathe and count."
    ]
    #stress_level = int(stress_level)
    #result = responses[min(stress_level-1,9)]
    result = chatGPT(stress_level)
    file = text_to_wav_cli(result)
    return file


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
