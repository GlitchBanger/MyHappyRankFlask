# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
import base64
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from openai import OpenAI
from gtts import gTTS
import io
from pydub import AudioSegment
import speech_recognition as sr
import soundfile
# import numpy as np
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

# openai.api_key = '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'

client = OpenAI()

# Flask constructor takes the name of 
# current module (__name__) as argument.
app = Flask(__name__)

cors = CORS(app)

# The route() function of the Flask class is a decorator, 
# which tells the application which URL should call 
# the associated function.
@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
	return 'Hello World'

@app.route('/getquestion')
def getquestion():
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Ask me a question for my psychometic test."}
        ]
    )
    question = str(completion.choices[0].message.content.split(':')[-1])
    myobj = gTTS(text=question, lang='en', slow=False)
    myobj.save('./output.mp3')
    sound = AudioSegment.from_mp3("output.mp3")
    sound.export('output.wav', format='wav')
    with open('./output.wav', 'rb') as f:
        buffer = io.BytesIO(f.read())
    buffer = base64.b64encode(buffer.getvalue()).decode()
    print(question)
    return jsonify({"text": question, "soundarray": buffer})
    # return question
    
@app.route('/gettext', methods=['POST'])
def gettext():
    if request.method == 'POST':
        url = request.json.get('file')
        decoded = base64.b64decode(url.split(',', 1)[1])
        with open("temp.wav", "wb") as file:
            file.write(decoded)
        data, samplerate = soundfile.read("temp.wav")
        soundfile.write("temp.wav", data, samplerate)
        r = sr.Recognizer()
        audio = sr.AudioFile("temp.wav")
        with audio as source:
            recording = r.record(source)                  
        result = r.recognize_google(recording)
        print(result)
        return jsonify({"output": result})


# main driver function
if __name__ == '__main__':

	# run() method of Flask class runs the application 
	# on the local development server.
	app.run(host="0.0.0.0", port=8000)
