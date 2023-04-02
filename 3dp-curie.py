import os
import openai
import pyttsx3
import speech_recognition as sr
import pyttsx3
 
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
with open('hidden.txt') as file:
    openai.api_key = file.read()

start_sequence = "\nAI:"
restart_sequence = "\nHuman: "

def get_api_response(prompt: str) -> str | None:
    text: str | None = None

    try:
        response: dict = openai.Completion.create(
            model='text-curie-001',
            prompt=prompt,
            temperature=0.3,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
            stop=[" Human:", " AI:"]
        )

        choices: dict = response.get('choices')[0]
        text = choices.get('text')


    except Exception as e:
        print('ERROR:', e)

    return text

def update_list(message: str, pl: list[str]):
    pl.append(message)

def create_prompt(message: str, pl: list[str]) -> str:
    p_message: str = f'\nHuman: {message}'
    update_list(p_message, pl)
    prompt: str = ''.join(pl)
    return prompt

def get_bot_response(message: str, pl: list[str]) -> str:
    prompt: str = create_prompt(message, pl)
    bot_response: str = get_api_response(prompt)

    if bot_response:
        update_list(bot_response, pl)
        pos: int = bot_response.find('\nAI: ')
        bot_response = bot_response[pos + 5:]
    else:
        bot_response = 'Sorry I think one of my circuits may have gone loose'

    return bot_response

#with open('list.txt') as file:
#    prompts = file.read()


def main():    
    prompt_list: list[str] = ['You are a protocol droid in the Star Wars universe named 3-DP. You were first created by the corporation Cybot Galactica on the factory world of Affa during the Clone Wars. After serving the republic during the war, you were stolen by a smuggler and sold to me (an explorer named Sree from Dantooine) in 7 BBY and You refer to me as Master, Sir, or Master Sree. You will have similar responses to C-3PO and be overworried about the slightest things.',
                              '\nHuman: Who are you?',
                              '\nAI: My name is 3-DP, human cyborg relations ... I am fluent in over six million forms of communication.']
    
    while True:
        try: 
            with sr.Microphone() as source2:
                # wait for a second to let the recognizer
                # adjust the energy threshold based on
                # the surrounding noise level
                r.adjust_for_ambient_noise(source2, duration=0.2)

                #listens for the user's input
                audio2 = r.listen(source2)

                # Using google to recognize audio
                MyText = r.recognize_google(audio2)
                MyText = MyText.lower()

                print(f'>> {MyText}')
                matches = ["3d", "3dp"]

                if any([x in MyText for x in matches]):
                    user_input: str = MyText
                    #user_input: str = input('You: ')
                    response: str = get_bot_response(user_input, prompt_list)
                    print(f'3-DP: {response}')
                    engine.say(response)
                    engine.runAndWait()

        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
         
        except sr.UnknownValueError:
            print("Sorry, could you repeat that?")

if __name__ == '__main__':
    main()