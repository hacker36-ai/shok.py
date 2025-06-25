import os, platform, subprocess, datetime, time, logging
import speech_recognition as sr
import pyttsx3
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
API_KEY = "insert-your-own"
if not API_KEY:
    exit("❌ Error: GOOGLE_API_KEY not found in environment.")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
chat_session = model.start_chat()

# Voice setup
engine = pyttsx3.init()
voices = engine.getProperty("voices")
uk_voice = next((v for v in voices if "english" in v.name.lower()), voices[0])
engine.setProperty('voice', uk_voice.id)
engine.setProperty('rate', 170)

def speak(text):
    print(f"SHOK: {text}")
    engine.say(text)
    engine.runAndWait()

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def wait_for_wake(self):
        with sr.Microphone() as src:
            self.recognizer.adjust_for_ambient_noise(src, duration=0.4)
            while True:
                print("⏳ Awaiting code word...")
                audio = self.recognizer.listen(src, timeout=None, phrase_time_limit=3)
                try:
                    phrase = self.recognizer.recognize_google(audio).lower()
                    if "1503" in phrase:
                        speak("Yes, Commander?")
                        return
                except:
                    pass

    def listen(self):
        with sr.Microphone() as src:
            self.recognizer.adjust_for_ambient_noise(src, duration=0.3)
            audio = self.recognizer.listen(src, timeout=5, phrase_time_limit=5)
            try:
                return self.recognizer.recognize_google(audio).lower()
            except:
                speak("Repeat, Commander.")
                return ""

class SHOK:
    def __init__(self):
        self.voice = VoiceAssistant()

    def ask_gemini(self, prompt):
        try:
            resp = chat_session.send_message(prompt)
            return resp.text
        except Exception as e:
            logging.error(f"Gemini error: {e}")
            return "Gemini is offline, Commander."

    def close_window(self):
        sys = platform.system()
        if sys == "Windows":
            import win32gui, win32con
            hwnd = win32gui.GetForegroundWindow()
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        elif sys == "Darwin":
            subprocess.run(['osascript', '-e', 'tell application "System Events" to keystroke "w" using {command down}'])
        else:
            subprocess.run(['xdotool', 'key', 'alt+F4'])
        speak("Window closed, Commander.")

    def take_screenshot(self):
        filename = f"screenshot_{int(time.time())}.png"
        if platform.system() == "Windows":
            subprocess.run(['powershell', '-Command', 'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait("%{PRTSC}")'])
        else:
            subprocess.run(['scrot', filename])
        speak(f"Screenshot saved: {filename}")

    def execute(self, cmd):
        if any(kw in cmd for kw in ["time", "what time is it"]):
            now = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"It’s {now}, Commander.")
        elif "open youtube" in cmd:
            speak("Opening YouTube.")
            os.system("start https://www.youtube.com")
        elif cmd.startswith("open ") or cmd.startswith("launch "):
            app = cmd.split(" ", 1)[1]
            try:
                speak(f"Launching {app}.")
                if platform.system() == "Windows":
                    os.startfile(app)
                else:
                    subprocess.Popen([app])
            except:
                speak("Target not located.")
        elif "quote" in cmd or "inspire me" in cmd:
            speak("Retrieving inspiration...")
            speak(self.ask_gemini("Give one short motivational quote."))
        elif "joke" in cmd:
            speak("Brace yourself...")
            speak(self.ask_gemini("Tell me a witty joke under 20 words."))
        elif "close window" in cmd:
            self.close_window()
        elif "screenshot" in cmd:
            self.take_screenshot()
        elif "self destruct" in cmd:
            speak("Initiating dramatic countdown. 3...2...1... Just kidding.")
        elif "who are you" in cmd or "what are you" in cmd:
            speak("I’m SHOK—Strategic Hybrid Operations Kompanion.")
        elif "shutdown" in cmd or "terminate" in cmd:
            speak("Standing down, Commander.")
            return False
        else:
            speak("Processing...")
            speak(self.ask_gemini(f"The user said: '{cmd}'. Respond concisely and confidently."))
        return True

    def activate(self):
        speak("SHOK 1.0 online. Awaiting command, Commander.")
        run = True
        while run:
            self.voice.wait_for_wake()
            command = self.voice.listen()
            if command:
                run = self.execute(command)
            time.sleep(0.4)

if __name__ == "__main__":
    SHOK().activate()
