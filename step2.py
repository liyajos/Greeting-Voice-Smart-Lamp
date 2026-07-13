import speech_recognition as sr

# Create a recognizer object.. this is what converts speech to text
r = sr.Recognizer()

# Create a microphone object.. this accesses your earbuds mic
mic = sr.Microphone()

# Open the microphone
with mic as source:
    # Listen to background noise for 1 second to understand silence level
    r.adjust_for_ambient_noise(source, duration=1)
    print("Listening... speak now.")
    # Record what you say (wait max 5 seconds)
    audio = r.listen(source, timeout=5, phrase_time_limit=5)

# Try to convert the audio to text
try:
    text = r.recognize_google(audio)  # Sends audio to Google's servers
    print(f"You said: {text}")
except sr.UnknownValueError:
    print("Could not understand audio")  # Couldn't make out what you said
except sr.RequestError as e:
    print(f"API error: {e}")  # Internet problem