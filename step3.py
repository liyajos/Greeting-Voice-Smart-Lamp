import speech_recognition as sr
from gpiozero import RGBLED
from time import sleep

# Connect to the RGB LED on GPIO pins 17 (red), 27 (green), 22 (blue)
led = RGBLED(red=17, green=27, blue=22)

# Set up speech recognition
r = sr.Recognizer()
mic = sr.Microphone()

# Dictionary of color names ? (Red, Green, Blue) values (0 to 1 scale)
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
    """Look at the text and decide what command was given"""
    t = text.lower()  # Convert to lowercase so "Red" and "red" both work
    
    if "off" in t:
        return ("off", None)
    if "on" in t:
        return ("on", (1, 0.7, 0.3))  # Warm white when turned on
    for name, rgb in COLORS.items():
        if name in t:
            return ("color", rgb)
    if "rainbow" in t or "party" in t:
        return ("rainbow", None)
    
    return (None, None)  # No matching command found

def execute(cmd, arg):
    """Run the command on the LED"""
    if cmd == "off":
        led.off()
    elif cmd == "on":
        led.color = arg
    elif cmd == "color":
        led.color = arg
    elif cmd == "rainbow":
        # Cycle through all colors with a short pause
        for c in COLORS.values():
            led.color = c
            sleep(0.3)
        led.off()
    else:
        print("(no matching command)")

# Calibrate for background noise once at the start
with mic as source:
    r.adjust_for_ambient_noise(source, duration=0.5)

print("Ready. Speak a command (e.g., 'turn on', 'make it blue', 'rainbow').")
print("Press Ctrl+C to quit.")

# Main loop..keeps listening forever until you press Ctrl+C
# Main loop..keeps listening forever until you press Ctrl+C
try:
    while True:
        with mic as source:
            audio = r.listen(source, phrase_time_limit=2)

        try:
            text = r.recognize_google(audio)
            print(f"Heard: {text}")
            cmd, arg = parse(text)
            execute(cmd, arg)

        except sr.UnknownValueError:
            pass  # Ignore when it can't understand, just try again

        except sr.RequestError as e:
            print(f"API error: {e}")

except KeyboardInterrupt:
    print("\nProgram stopped by user.")

finally:
    led.off()
    led.close()