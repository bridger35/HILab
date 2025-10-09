**Pipeline Summary:**

 The Turbosatori to Metahuman pipeline runs in real time to procure and analyze Turbosatori’s outputs before sending the processed data to Unreal to generate a unique Metahuman reaction based on participants’ stress level.

**Step by Step Functionality:**
	
 The initial process utilizes a python script with the Turbosatori Network Interface(TVI) library whose encode/decode features were updated to match Expyriment 1.0.0 and newer versions of python. The provided functions in TVI are then used to pull data from Turbosatori and translate that data into a stress level. This stress level is then sent to an API python script via HTTP POST on a machine running the Unreal environment locally. The API then uses the OpenAI library to generate a mindfulness intervention through roleplaying with ChatGPT. The text output is then converted to a MP3 using gTTS library before using ffmpeg to convert to a high quality WAV. The file path is then sent to Unreal through an HTTP GET request issued from Unreal and passed to Nvidia ACE for A2F to act on the metahuman. 
