import speech_recognition as sr
from gpiozero import RGBLED, Button
from time import sleep
import threading

led = RGBLED(red=17, green=27, blue=22)
button = Button(21)
r = sr.Recognizer()
mic = sr.Microphone()

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

# This stores the last commanded color (so we can restore it after feedback)
last_color = None

def parse(text):
    t = text.lower()
    if "off" in t: return ("off", None)
    if "on" in t: return ("on", (1, 0.7, 0.3))
    for name, rgb in COLORS.items():
        if name in t: return ("color", rgb)
    if "rainbow" in t or "party" in t: return ("rainbow", None)
    return (None, None)

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
            led.color = c; sleep(0.3)
        led.off()
        last_color = None
    else:
        # Orange flash = understood but no matching command
        led.color = (1, 0.5, 0); sleep(0.3)
        # Restore previous color
        if last_color: led.color = last_color
        else: led.off()

def flash_green():
    """Brief green flash = success"""
    led.color = (0, 1, 0)
    sleep(0.3)

def flash_red():
    """Brief red flash = didn't understand"""
    led.color = (0.3, 0, 0)
    sleep(0.3)
    led.off()

def pulse_yellow():
    """Dim yellow = processing"""
    led.color = (0.3, 0.3, 0)

# Calibrate once
with mic as source:
    r.adjust_for_ambient_noise(source, duration=1)

print("=== Voice Smart Lamp Ready ===")
print("LED States:")
print("  OFF      = idle, waiting for button")
print("  DIM BLUE = listening to your voice")
print("  DIM YELLOW = processing / sending to Google")
print("  GREEN FLASH = command understood!")
print("  RED FLASH = couldn't understand")
print("  ORANGE FLASH = no matching command")
print("")
print("Press and hold the button, speak, then release.")
print("Press Ctrl+C to quit.")

try:
    while True:
        # State: IDLE   LED is off, waiting for button
        if last_color:
            led.color = last_color
        else:
            led.off()

        button.wait_for_press()

        # State: LISTENING   dim blue
        led.color = (0, 0, 0.3)
        print("Listening...")

        with mic as source:
            try:
                audio = r.listen(source, timeout=3, phrase_time_limit=5)
            except sr.WaitTimeoutError:
                print("No speech detected.")
                led.off()
                continue

        # State: PROCESSING   dim yellow
        pulse_yellow()
        print("Processing...")

        try:
            text = r.recognize_google(audio)
            print(f"Heard: '{text}'")

            cmd, arg = parse(text)

            if cmd is None:
                # Orange flash = recognized speech but no command matched
                led.color = (1, 0.5, 0)
                sleep(0.3)
                print("(No matching command)")
                led.off()
            else:
                # Green flash = success
                flash_green()
                execute(cmd, arg)

                print("Command =", cmd)
                print("Argument =", arg)
                print("LED color =", led.color)

                print(f"Executed: {cmd}")

        except sr.UnknownValueError:
            # Red flash = couldn't understand audio
            flash_red()
            print("Could not understand.")

        except sr.RequestError as e:
            # Network/API error
            flash_red()
            print(f"API error: {e}")

        sleep(2)

        # Wait for button to be released before next cycle
        button.wait_for_release()

except KeyboardInterrupt:
    print("\nProgram stopped by user.")

finally:
    led.off()
    led.close()