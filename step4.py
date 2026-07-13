import speech_recognition as sr
from gpiozero import RGBLED, Button
from time import sleep

led = RGBLED(red=17, green=27, blue=22)
button = Button(21)  # Button on GPIO 21, internal pull-up enabled automatically

r = sr.Recognizer()
mic = sr.Microphone()

# Same colors as before
COLORS = {
    "red":    (1, 0, 0),
    "green":  (0, 1, 0),
    "blue":   (0, 0, 1),
    "yellow": (1, 1, 0),
    "purple": (0.5, 0, 1),
    "white":  (1, 1, 1),
    "orange": (1, 0.5, 0),
    "pink":   (1, 0.4, 0.6),
    "cyan":    (0, 1, 1),
    "magenta": (1, 0, 1),
    "lime":    (0.5, 1, 0),
    "teal":    (0, 0.5, 0.5),
    "gold":    (1, 0.84, 0),
    "lavender": (0.7, 0.5, 1),
    "mint":    (0.2, 1, 0.6),
    "coral":   (1, 0.4, 0.3),
    "maroon":  (0.5, 0, 0),
    "navy":    (0, 0, 0.5),

}

def parse(text):
    t = text.lower()
    if "off" in t: return ("off", None)
    if "on" in t: return ("on", (1, 0.7, 0.3))
    for name, rgb in COLORS.items():
        if name in t: return ("color", rgb)
    if "rainbow" in t or "party" in t: return ("rainbow", None)
    return (None, None)

def execute(cmd, arg):
    if cmd == "off": led.off()
    elif cmd == "on": led.color = arg
    elif cmd == "color": led.color = arg
    elif cmd == "rainbow":
        for c in COLORS.values():
            led.color = c; sleep(0.3)
        led.off()
    else: print("(no matching command)")

# Visual feedback when button is pressed/released
def on_press():
    led.color = (0, 0, 0.3)  # Dim blue = "I'm listening"
    print("Listening...")

def on_release():
    led.off()  # Turn off while processing

button.when_pressed = on_press
button.when_released = on_release

# Calibrate background noise
with mic as source:
    r.adjust_for_ambient_noise(source, duration=1)

print("Press and hold the button, speak, then release.")
print("Press Ctrl+C to quit.")

try:
    while True:
        button.wait_for_press()  # Do nothing until button is pressed

        with mic as source:
            try:
                audio = r.listen(source, timeout=2, phrase_time_limit=4)
            except sr.WaitTimeoutError:
                continue  # No speech heard, go back to waiting

        try:
            text = r.recognize_google(audio)
            print(f"Heard: {text}")
            cmd, arg = parse(text)
            execute(cmd, arg)

        except sr.UnknownValueError:
            # Flash red = didn't understand
            led.color = (0.3, 0, 0)
            sleep(0.3)
            led.off()

        except sr.RequestError as e:
            print(f"API error: {e}")

except KeyboardInterrupt:
    print("\nProgram stopped by user.")

finally:
    led.off()
    led.close()