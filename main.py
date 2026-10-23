import datetime
import math
import os
import threading
import tkinter as tk
import webbrowser
import cv2
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import win32com.client
from dotenv import load_dotenv
from google import genai
import wikipedia

# Load API Key from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = None
if api_key:
  try:
    client = genai.Client(api_key=api_key)
  except Exception as e:
    print(f"Gemini init error: {e}")

# Initialize Windows SAPI Voice

speaker = win32com.client.Dispatch("SAPI.SpVoice")



class JarvisPyCharmApp:

  def __init__(self, root):
    self.root = root
    self.root.title("J.A.R.V.I.S. - Core HUD Interface")
    self.root.geometry("540x680")
    self.root.configure(bg="#050b14")  # Deep Iron Man dark theme

    # Title Header
    self.title_label = tk.Label(
        root,
        text="J.A.R.V.I.S. PROTOCOL",
        font=("Consolas", 16, "bold"),
        fg="#00ffff",
        bg="#050b14",
    )
    self.title_label.pack(pady=10)

    # Glowing Animated Arc Reactor HUD Canvas
    self.canvas = tk.Canvas(
        root, width=200, height=200, bg="#050b14", highlightthickness=0
    )
    self.canvas.pack(pady=5)
    self.angle = 0
    self.animate_hud()  # Start the rotating blue HUD loop

    # Status Display
    self.status_label = tk.Label(
        root,
        text="Status: Standby",
        font=("Consolas", 11),
        fg="#00ffcc",
        bg="#050b14",
    )
    self.status_label.pack(pady=5)

    # Chat / Terminal Log Box
    self.text_box = tk.Text(
        root,
        width=60,
        height=12,
        font=("Consolas", 10),
        bg="#070e1a",
        fg="#00ffff",
        insertbackground="white",
        highlightbackground="#0055ff",
        highlightthickness=1,
    )
    self.text_box.pack(pady=10)
    self.log_message(
        "JARVIS: All local systems online and synchronized, Ma'am."
    )

    if not api_key:
      self.log_message(
          "WARNING: GEMINI_API_KEY missing in .env file! AI chat will be"
          " disabled."
      )

    # Big Sci-Fi Activation Button
    self.listen_btn = tk.Button(
        root,
        text="🎤 ACTIVATE VOICE COMMAND",
        command=self.start_listening_thread,
        font=("Consolas", 12, "bold"),
        bg="#00ffff",
        fg="#050b14",
        activebackground="#00b3b3",
        padx=20,
        pady=8,
        relief="flat",
        cursor="hand2",
    )
    self.listen_btn.pack(pady=10)

  def animate_hud(self):
    """Draws and rotates the multi-layered glowing blue arc reactor rings"""
    self.canvas.delete("hud")
    cx, cy = 100, 100

    # Outer spinning tech segments
    for i in range(4):
      start = self.angle + (i * 90)
      self.canvas.create_arc(
          30,
          30,
          170,
          170,
          start=start,
          extent=40,
          outline="#00d2ff",
          width=3,
          style="arc",
          tags="hud",
      )

    # Counter-spinning middle ring
    for i in range(3):
      start = -self.angle * 1.5 + (i * 120)
      self.canvas.create_arc(
          50,
          50,
          150,
          150,
          start=start,
          extent=60,
          outline="#0055ff",
          width=2,
          style="arc",
          tags="hud",
      )

    # Inner stable glowing core
    self.canvas.create_oval(
        75,
        75,
        125,
        125,
        outline="#00ffff",
        width=2,
        fill="#071a3a",
        tags="hud",
    )
    self.canvas.create_oval(
        88,
        88,
        112,
        112,
        fill="#00ffcc",
        outline="",
        tags="hud",
    )

    # Increment rotation angle
    self.angle = (self.angle + 3) % 360
    self.root.after(40, self.animate_hud)  # Smooth 25 FPS rotation loop

  def log_message(self, message):
    self.text_box.insert("end", f"{message}\n")
    self.text_box.see("end")

  def speak(self, text):
    self.log_message(f"JARVIS: {text}")
    self.status_label.config(text="Status: Speaking...")
    if speaker:
      speaker.Speak(text)
    self.status_label.config(text="Status: Standby")

  def start_listening_thread(self):
    threading.Thread(target=self.run_jarvis_logic, daemon=True).start()

  def run_jarvis_logic(self):
    self.listen_btn.config(state="disabled", text="LISTENING...")
    self.status_label.config(text="Status: Listening...")

    samplerate = 16000
    duration = 5
    filename = "temp_recording.wav"

    try:
      audio_data = sd.rec(
          int(duration * samplerate),
          samplerate=samplerate,
          channels=1,
          dtype="int16",
      )
      sd.wait()
      sf.write(filename, audio_data, samplerate)

      self.status_label.config(text="Status: Recognizing...")
      r = sr.Recognizer()
      with sr.AudioFile(filename) as source:
        audio = r.record(source)
      query = r.recognize_google(audio, language="en-IN")
      self.log_message(f"User: {query}")
      self.process_command(query.lower())

    except Exception:
      self.log_message("JARVIS: Could not understand audio.")
      self.speak("Could not understand audio. Please try again.")
    finally:
      if os.path.exists(filename):
        os.remove(filename)
      self.listen_btn.config(state="normal", text="🎤 ACTIVATE VOICE COMMAND")
      self.status_label.config(text="Status: Standby")

  def process_command(self, query):
    if "stop" in query or "exit" in query or "goodbye" in query:
      self.speak("Goodbye. Shutting down systems.")
      self.root.destroy()

    elif "open youtube" in query:
      self.speak("Opening YouTube for you, Ma'am.")
      webbrowser.open("https://www.youtube.com")

    elif "the time" in query:
      strfTime = datetime.datetime.now().strftime("%H:%M:%S")
      self.speak(f"The current time is {strfTime}")

    elif "wikipedia" in query or "search for" in query:
      self.speak("Searching Wikipedia...")
      search_term = (
          query.replace("wikipedia", "")
          .replace("search for", "")
          .replace("jarvis", "")
          .strip()
      )
      try:
        results = wikipedia.summary(search_term, sentences=2)
        self.speak(results)
      except Exception:
        self.speak("I couldn't find a matching article on Wikipedia.")

    elif "open camera" in query:
      self.speak("Opening camera. Press q to close.")
      cap = cv2.VideoCapture(0)
      if cap.isOpened():
        while True:
          ret, frame = cap.read()
          if not ret:
            break
          cv2.imshow("Jarvis Camera Feed", frame)
          if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        cap.release()
        cv2.destroyAllWindows()
      self.speak("Camera closed.")

    else:
      if not client:
        self.speak("AI brain not connected. Check your .env file.")
        return

      self.status_label.config(text="Status: Thinking...")
      try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=(
                "You are JARVIS, a witty, helpful AI assistant. Keep responses"
                " short and conversational in 1 to 2 sentences."
                f" User query: {query}"
            ),
        )
        self.speak(response.text)
      except Exception as e:
        print(f"DEBUG ERROR: {e}")
        self.speak("I encountered an error connecting to my neural network.")


if __name__ == "__main__":
  root = tk.Tk()
  app = JarvisPyCharmApp(root)
  root.mainloop()