import speech_recognition as sr
from gpiozero import RGBLED, Button
from time import sleep

# -------------------------------
# Hardware Setup
# -------------------------------
led = RGBLED(red=17, green=27, blue=22)
button = Button(21)

r = sr.Recognizer()
mic = sr.Microphone()

# -------------------------------
# Available LED Colors
# -------------------------------
COLORS = {
    "red": (1, 0, 0),
    "green": (0, 1, 0),
    "blue": (0, 0, 1),
    "yellow": (1, 1, 0),
    "purple": (0.5, 0, 1),
    "white": (1, 1, 1),
    "orange": (1, 0.5, 0),
    "pink": (1, 0.4, 0.6),
}

last_color = None

# -------------------------------
# Parse Voice Commands
# -------------------------------
def parse(text):
    t = text.lower()

    if "off" in t:
        return ("off", None)

    if "on" in t:
        return ("on", (1, 0.7, 0.3))

    if "hello" in t or "hi" in t:
        return ("hello", None)

    if "good morning" in t:
        return ("morning", None)

    if "good afternoon" in t:
        return ("afternoon", None)

    if "good evening" in t:
        return ("evening", None)

    if "good night" in t:
        return ("night", None)

    if "thank you" in t:
        return ("thanks", None)

    for name, rgb in COLORS.items():
        if name in t:
            return ("color", rgb)

    if "rainbow" in t or "party" in t:
        return ("rainbow", None)

    return (None, None)


# -------------------------------
# Execute Commands
# -------------------------------
def execute(cmd, arg):
    global last_color

    if cmd == "off":
        last_color = None
        led.off()

    elif cmd in ("on", "color"):
        last_color = arg
        led.color = arg

    elif cmd == "rainbow":
        for c in COLORS.values():
            led.color = c
            sleep(0.3)
        led.off()

    elif cmd == "hello":
        print("Hello! Nice to meet you!")
        for _ in range(2):
            led.color = (0, 1, 0)
            sleep(0.3)
            led.off()
            sleep(0.3)

    elif cmd == "morning":
        print("Good Morning!")
        led.color = (1, 1, 0)
        sleep(2)
        led.off()

    elif cmd == "afternoon":
        print("Good Afternoon!")
        led.color = (1, 0.5, 0)
        sleep(2)
        led.off()

    elif cmd == "evening":
        print("Good Evening!")
        led.color = (1, 0, 1)
        sleep(2)
        led.off()

    elif cmd == "night":
        print("Good Night!")
        led.color = (0, 0, 1)
        sleep(2)
        led.off()

    elif cmd == "thanks":
        print("You're Welcome!")
        for _ in range(3):
            led.color = (0, 1, 0)
            sleep(0.2)
            led.off()
            sleep(0.2)


# -------------------------------
# Microphone Calibration
# -------------------------------
with mic as source:
    r.adjust_for_ambient_noise(source, duration=1)

print("===================================")
print(" Greeting Voice Smart Lamp ")
print("===================================")
print("Supported Greeting Commands:")
print("  Hello")
print("  Good Morning")
print("  Good Afternoon")
print("  Good Evening")
print("  Good Night")
print("  Thank You")
print("")
print("Color Commands:")
print("  Red, Green, Blue, Yellow")
print("  Purple, Pink, Orange, White")
print("  Rainbow")
print("  Turn On")
print("  Turn Off")
print("")
print("Press and hold the button, speak, then release.")
print("-----------------------------------")

# -------------------------------
# Main Loop
# -------------------------------
try:
    while True:

        led.off()

        button.wait_for_press()

        # Listening
        led.color = (0, 0, 0.3)
        print("\nListening...")

        with mic as source:
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
            except sr.WaitTimeoutError:
                print("No speech detected.")
                led.off()
                button.wait_for_release()
                continue

        # Processing
        led.color = (0.3, 0.3, 0)
        print("Processing...")

        try:
            text = r.recognize_google(audio)
            print(f"Heard: {text}")

            cmd, arg = parse(text)

            if cmd is None:
                print("No matching command.")
                led.color = (1, 0.5, 0)
                sleep(0.5)
                led.off()

            else:
                execute(cmd, arg)
                print(f"Executed: {cmd}")

        except sr.UnknownValueError:
            print("Could not understand audio.")
            led.color = (0.3, 0, 0)
            sleep(0.5)
            led.off()

        except sr.RequestError as e:
            print("API Error:", e)
            led.color = (0.3, 0, 0)
            sleep(0.5)
            led.off()

        button.wait_for_release()

except KeyboardInterrupt:
    print("\nProgram stopped by user.")

finally:
    led.off()
    led.close()