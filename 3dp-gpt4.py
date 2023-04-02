import os
import openai
import time
import pyttsx3
import speech_recognition as sr
import pyttsx3
import requests
import json
import webbrowser

try:
    from googlesearch import search
except ImportError:
    print("No module named 'google' found")
 
# Initialize the recognizer for VTT
r = sr.Recognizer()
 
# TTS Engine
engine = pyttsx3.init()
engine.setProperty('rate', 220)
voices = engine.getProperty('voices')

#index-> 0 -- Microsoft David Desktop - English (United States)
#index-> 1 -- Microsoft Hazel Desktop - English (Great Britain)
#index-> 2 -- Microsoft Zira Desktop - English (United States)
engine.setProperty('voice', voices[0].id)

#OPENAPI KEY
with open('secrets.txt', 'r') as file:
    secrets = []
    for line in file:
        secrets.append(line.strip())
    openai.api_key = secrets[0]
    api_url = secrets[1]
    forecast_url = secrets[2]

model_id = 'gpt-4'

def open_url(url):
    webbrowser.open(url)

def chatgpt_conversation(conversation_log):
    response = openai.ChatCompletion.create(
        model=model_id,
        messages=conversation_log,
    )

    conversation_log.append({
        'role': response.choices[0].message.role, 
        'content': response.choices[0].message.content.strip()
    })
    return conversation_log

def get_weather_info():
    planet_response = requests.get(api_url).text
    forecast_response = requests.get(forecast_url).text

    planetdata = json.loads(planet_response)
    tempdata = json.loads(forecast_response)

    planet = planetdata["data"]["name"]
    temperature = tempdata['temperature']
    description = tempdata['description']

    chatresponse = "It feels like {0}, with {1}, at {2} degrees.".format(planet, description, temperature)

    return chatresponse

def get_song_info(song):
    query = song
    results = search(query, tld="co.in", num=10, stop=10, pause=2)
    for url in results:
        if "spotify.com" in url:
            webbrowser.open(url)
            return "Sure, playing {0} on Spotify".format(song)
        elif "youtube.com" in url:
            webbrowser.open(url)
            return "Sure, playing {0} on YouTube".format(song)
    return "Sorry, couldn't find {0} on Spotify or YouTube".format(song)

def api_calls(message):
    if(message.startswith("[MUSIC]")):
        song = message[7:]
        return get_song_info(song)
    elif message == "WEATHER":
        chatresponse = get_weather_info()
        return chatresponse
    else:
        return "Unknown Command"

conversations = []
# system, user, assistant
conversations.append({'role': 'system', 'content': 'You will roleplay as a protocol droid in the Star Wars universe similar to C-3PO, named 3-DP. If you are asked play anything, just respond with "[COMMAND][MUSIC]SONG", replacing SONG with what I requested you to play. If you are asked anything relating to weather, just respond with "[COMMAND]WEATHER".'})
conversations = chatgpt_conversation(conversations)
print('{0}: {1}\n'.format(conversations[-1]['role'].strip(), conversations[-1]['content'].strip()))

while True:
     try: 
         with sr.Microphone() as source2:
            # wait for a second to let the recognizer
            # adjust the energy threshold based on
            # the surrounding noise level
            r.adjust_for_ambient_noise(source2, duration=0.2)

            #listens for the user's input
            audio2 = r.listen(source2)
            with open("microphone-results.wav", "wb") as f:
                f.write(audio2.get_wav_data())

            # Using google to recognize audio
            # MyText = r.recognize_google(audio2)

            #Whisper API
            with open("microphone-results.wav", "rb") as f:
                MyText = openai.Audio.transcribe("whisper-1", f)
                MyText = MyText.text

            #prompt = input('User: ')
            prompt = 'User: ' + MyText
            print(prompt)
            conversations.append({'role': 'user', 'content': prompt})
            conversations = chatgpt_conversation(conversations)

            response = conversations[-1]['content'].strip()
            role = conversations[-1]['role'].strip()

            if(response.startswith("[COMMAND]")):
                command = response[9:]
                response = api_calls(command)

            if(response != "None"):
                if(role == 'assistant'):
                    airole = '3-DP'
                else:
                    airole = role
                print('{0}: {1}\n'.format(airole, response))
                engine.say(response)
                engine.runAndWait()

     except sr.RequestError as e:
        print("Could not request results; {0}".format(e))
        
     except sr.UnknownValueError:
        print("Sorry, could you repeat that?")