import os
import whisper
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, simpledialog
import warnings
from fpdf import FPDF
from docx import Document
import yt_dlp  # YouTube Downloader

warnings.simplefilter("ignore")

# Load Whisper model (smallest version for faster processing)
model = whisper.load_model("tiny")

def transcribe_file():
    """Handles file selection and starts transcription in a separate thread."""
    file_path = filedialog.askopenfilename(
        title="Select an Audio/Video File",
        filetypes=[("Media Files", "*.mp3 *.wav *.mp4 *.mkv *.avi")]
    )
    
    if not file_path:
        return  # No file selected

    # Run transcription in a separate thread
    thread = threading.Thread(target=process_transcription, args=(file_path,))
    thread.start()

def transcribe_youtube():
    """Downloads YouTube audio and transcribes it."""
    youtube_url = simpledialog.askstring("YouTube Link", "Enter YouTube video URL:")
    
    if not youtube_url:
        return

    # Download and process in a separate thread
    thread = threading.Thread(target=download_and_transcribe, args=(youtube_url,))
    thread.start()

def download_and_transcribe(youtube_url):
    """Downloads YouTube video as audio and transcribes it."""
    try:
        # Show progress message
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, "Downloading YouTube audio... Please wait.")

        # Define download options
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "outtmpl": "youtube_audio.%(ext)s"  # Save as youtube_audio.mp3
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        file_path = "youtube_audio.mp3"  # Audio file path

        # Start transcription
        process_transcription(file_path)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to download: {e}")

def process_transcription(file_path):
    """Runs the Whisper transcription process in a separate thread."""
    try:
        # Show a "Processing..." message
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, "Processing... Please wait.")

        # Transcribe file
        result = model.transcribe(file_path)
        transcript = result["text"]

        # Update UI with transcription
        text_area.delete(1.0, tk.END)
        text_area.insert(tk.END, transcript)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to transcribe: {e}")

def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(text_area.get(1.0, tk.END))
    root.update()
    messagebox.showinfo("Copied", "Transcription copied to clipboard!")

def save_as_pdf():
    text = text_area.get(1.0, tk.END).strip()
    if not text:
        messagebox.showwarning("Warning", "No text to save!")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                             filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(190, 10, text)
        pdf.output(file_path)
        messagebox.showinfo("Saved", f"PDF saved successfully!\n{file_path}")

def save_as_word():
    text = text_area.get(1.0, tk.END).strip()
    if not text:
        messagebox.showwarning("Warning", "No text to save!")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".docx",
                                             filetypes=[("Word Documents", "*.docx")])
    if file_path:
        doc = Document()
        doc.add_paragraph(text)
        doc.save(file_path)
        messagebox.showinfo("Saved", f"Word document saved successfully!\n{file_path}")

# Create GUI window
root = tk.Tk()
root.title("Media & YouTube Transcription App")
root.geometry("700x500")

# Upload Button
upload_btn = tk.Button(root, text="Upload & Transcribe", command=transcribe_file, font=("Arial", 12))
upload_btn.pack(pady=10)

# YouTube Transcription Button
youtube_btn = tk.Button(root, text="Transcribe YouTube Video", command=transcribe_youtube, font=("Arial", 12))
youtube_btn.pack(pady=5)

# Text Box for Transcription Output
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 10), height=15)
text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Buttons Frame
buttons_frame = tk.Frame(root)
buttons_frame.pack(pady=10)

# Copy Button
copy_btn = tk.Button(buttons_frame, text="Copy to Clipboard", command=copy_to_clipboard, font=("Arial", 10))
copy_btn.grid(row=0, column=0, padx=5)

# Save as PDF Button
pdf_btn = tk.Button(buttons_frame, text="Save as PDF", command=save_as_pdf, font=("Arial", 10))
pdf_btn.grid(row=0, column=1, padx=5)

# Save as Word Button
word_btn = tk.Button(buttons_frame, text="Save as Word", command=save_as_word, font=("Arial", 10))
word_btn.grid(row=0, column=2, padx=5)

# Run the Tkinter main loop
root.mainloop()
