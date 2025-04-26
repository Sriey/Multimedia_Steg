import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import numpy as np
import pandas as pd
import os
import cv2
import wave
from matplotlib import pyplot as plt
import threading
import sys

class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Steganography Tool")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Create and configure the notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.home_tab = ttk.Frame(self.notebook)
        self.text_tab = ttk.Frame(self.notebook)
        self.image_tab = ttk.Frame(self.notebook)
        self.audio_tab = ttk.Frame(self.notebook)
        self.video_tab = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.home_tab, text="Home")
        self.notebook.add(self.text_tab, text="Text Steganography")
        self.notebook.add(self.image_tab, text="Image Steganography")
        self.notebook.add(self.audio_tab, text="Audio Steganography")
        self.notebook.add(self.video_tab, text="Video Steganography")
        
        # Set up the tabs
        self.setup_home_tab()
        self.setup_text_tab()
        self.setup_image_tab()
        self.setup_audio_tab()
        self.setup_video_tab()
        
        # Set up log console at the bottom
        self.console_frame = ttk.LabelFrame(root, text="Console Output")
        self.console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.console = scrolledtext.ScrolledText(self.console_frame, height=10)
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Redirect stdout to the console
        sys.stdout = TextRedirector(self.console)
    
    def setup_home_tab(self):
        title_label = ttk.Label(self.home_tab, 
                               text="STEGANOGRAPHY", 
                               font=("Arial", 24, "bold"))
        title_label.pack(pady=20)
        
        description = (
            "Welcome to the Steganography Tool!\n\n"
            "Steganography is the practice of hiding secret information within ordinary, non-secret data.\n"
            "This application supports hiding text in various media types:\n"
            "• Text files (using zero-width characters)\n"
            "• Image files (using LSB techniques)\n"
            "• Audio files (modifying audio data)\n"
            "• Video files (embedding in specific frames)\n\n"
            "Select a tab above to begin using the corresponding steganography technique."
        )
        
        desc_label = ttk.Label(self.home_tab, text=description, wraplength=700, justify="center")
        desc_label.pack(pady=20)
        
    def setup_text_tab(self):
        # Frame for encode/decode selection
        mode_frame = ttk.Frame(self.text_tab)
        mode_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(mode_frame, text="Operation:").pack(side=tk.LEFT, padx=5)
        
        self.text_mode = tk.StringVar(value="encode")
        ttk.Radiobutton(mode_frame, text="Encode", variable=self.text_mode, 
                        value="encode", command=self.update_text_mode).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Decode", variable=self.text_mode, 
                        value="decode", command=self.update_text_mode).pack(side=tk.LEFT, padx=10)
        
        # Frame for file selection
        file_frame = ttk.LabelFrame(self.text_tab, text="File Selection")
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(file_frame, text="Cover Text File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.cover_text_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.cover_text_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse", command=lambda: self.browse_file(self.cover_text_path, [("Text files", "*.txt")])).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(file_frame, text="Output File:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.text_output_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.text_output_path, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse", command=lambda: self.save_file(self.text_output_path, [("Text files", "*.txt")])).grid(row=1, column=2, padx=5, pady=5)
        
        # Frame for stego file (decode mode)
        self.text_stego_frame = ttk.LabelFrame(self.text_tab, text="Stego File")
        
        ttk.Label(self.text_stego_frame, text="Stego Text File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.stego_text_path = tk.StringVar()
        ttk.Entry(self.text_stego_frame, textvariable=self.stego_text_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.text_stego_frame, text="Browse", command=lambda: self.browse_file(self.stego_text_path, [("Text files", "*.txt")])).grid(row=0, column=2, padx=5, pady=5)
        
        # Frame for message input
        self.text_message_frame = ttk.LabelFrame(self.text_tab, text="Secret Message")
        self.text_message_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.text_message = scrolledtext.ScrolledText(self.text_message_frame, height=10)
        self.text_message.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame for buttons
        button_frame = ttk.Frame(self.text_tab)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Process", command=self.process_text_steganography).pack(side=tk.RIGHT, padx=10)
        
        # Initial mode setup
        self.update_text_mode()
    
    def setup_image_tab(self):
        # Frame for encode/decode selection
        mode_frame = ttk.Frame(self.image_tab)
        mode_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(mode_frame, text="Operation:").pack(side=tk.LEFT, padx=5)
        
        self.image_mode = tk.StringVar(value="encode")
        ttk.Radiobutton(mode_frame, text="Encode", variable=self.image_mode, 
                        value="encode", command=self.update_image_mode).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Decode", variable=self.image_mode, 
                        value="decode", command=self.update_image_mode).pack(side=tk.LEFT, padx=10)
        
        # Frame for file selection
        self.image_encode_frame = ttk.LabelFrame(self.image_tab, text="File Selection")
        self.image_encode_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(self.image_encode_frame, text="Cover Image:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.cover_image_path = tk.StringVar()
        ttk.Entry(self.image_encode_frame, textvariable=self.cover_image_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.image_encode_frame, text="Browse", command=lambda: self.browse_file(self.cover_image_path, [("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(self.image_encode_frame, text="Output Image:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.image_output_path = tk.StringVar()
        ttk.Entry(self.image_encode_frame, textvariable=self.image_output_path, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.image_encode_frame, text="Browse", command=lambda: self.save_file(self.image_output_path, [("Image files", "*.png")])).grid(row=1, column=2, padx=5, pady=5)
        
        # Frame for stego file (decode mode)
        self.image_decode_frame = ttk.LabelFrame(self.image_tab, text="Stego Image")
        
        ttk.Label(self.image_decode_frame, text="Stego Image:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.stego_image_path = tk.StringVar()
        ttk.Entry(self.image_decode_frame, textvariable=self.stego_image_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.image_decode_frame, text="Browse", command=lambda: self.browse_file(self.stego_image_path, [("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])).grid(row=0, column=2, padx=5, pady=5)
        
        # Frame for message input
        self.image_message_frame = ttk.LabelFrame(self.image_tab, text="Secret Message")
        self.image_message_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.image_message = scrolledtext.ScrolledText(self.image_message_frame, height=10)
        self.image_message.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame for buttons
        button_frame = ttk.Frame(self.image_tab)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Process", command=self.process_image_steganography).pack(side=tk.RIGHT, padx=10)
        
        # Initial mode setup
        self.update_image_mode()
    
    def setup_audio_tab(self):
        # Frame for encode/decode selection
        mode_frame = ttk.Frame(self.audio_tab)
        mode_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(mode_frame, text="Operation:").pack(side=tk.LEFT, padx=5)
        
        self.audio_mode = tk.StringVar(value="encode")
        ttk.Radiobutton(mode_frame, text="Encode", variable=self.audio_mode, 
                        value="encode", command=self.update_audio_mode).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Decode", variable=self.audio_mode, 
                        value="decode", command=self.update_audio_mode).pack(side=tk.LEFT, padx=10)
        
        # Frame for file selection
        self.audio_encode_frame = ttk.LabelFrame(self.audio_tab, text="File Selection")
        self.audio_encode_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(self.audio_encode_frame, text="Cover Audio:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.cover_audio_path = tk.StringVar()
        ttk.Entry(self.audio_encode_frame, textvariable=self.cover_audio_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.audio_encode_frame, text="Browse", command=lambda: self.browse_file(self.cover_audio_path, [("Wave files", "*.wav")])).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(self.audio_encode_frame, text="Output Audio:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.audio_output_path = tk.StringVar()
        ttk.Entry(self.audio_encode_frame, textvariable=self.audio_output_path, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.audio_encode_frame, text="Browse", command=lambda: self.save_file(self.audio_output_path, [("Wave files", "*.wav")])).grid(row=1, column=2, padx=5, pady=5)
        
        # Frame for stego file (decode mode)
        self.audio_decode_frame = ttk.LabelFrame(self.audio_tab, text="Stego Audio")
        
        ttk.Label(self.audio_decode_frame, text="Stego Audio:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.stego_audio_path = tk.StringVar()
        ttk.Entry(self.audio_decode_frame, textvariable=self.stego_audio_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.audio_decode_frame, text="Browse", command=lambda: self.browse_file(self.stego_audio_path, [("Wave files", "*.wav")])).grid(row=0, column=2, padx=5, pady=5)
        
        # Frame for message input
        self.audio_message_frame = ttk.LabelFrame(self.audio_tab, text="Secret Message")
        self.audio_message_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.audio_message = scrolledtext.ScrolledText(self.audio_message_frame, height=10)
        self.audio_message.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame for buttons
        button_frame = ttk.Frame(self.audio_tab)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Process", command=self.process_audio_steganography).pack(side=tk.RIGHT, padx=10)
        
        # Initial mode setup
        self.update_audio_mode()
    
    def setup_video_tab(self):
        # Frame for encode/decode selection
        mode_frame = ttk.Frame(self.video_tab)
        mode_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(mode_frame, text="Operation:").pack(side=tk.LEFT, padx=5)
        
        self.video_mode = tk.StringVar(value="encode")
        ttk.Radiobutton(mode_frame, text="Encode", variable=self.video_mode, 
                        value="encode", command=self.update_video_mode).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Decode", variable=self.video_mode, 
                        value="decode", command=self.update_video_mode).pack(side=tk.LEFT, padx=10)
        
        # Frame for file selection
        self.video_encode_frame = ttk.LabelFrame(self.video_tab, text="File Selection")
        self.video_encode_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(self.video_encode_frame, text="Cover Video:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.cover_video_path = tk.StringVar()
        ttk.Entry(self.video_encode_frame, textvariable=self.cover_video_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.video_encode_frame, text="Browse", command=lambda: self.browse_file(self.cover_video_path, [("Video files", "*.mp4;*.avi")])).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Label(self.video_encode_frame, text="Output Video:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.video_output_path = tk.StringVar(value="stego_video.mp4")
        ttk.Entry(self.video_encode_frame, textvariable=self.video_output_path, width=50).grid(row=1, column=1, padx=5, pady=5)
        
        # Frame for stego file and frame number (decode mode)
        self.video_decode_frame = ttk.LabelFrame(self.video_tab, text="Stego Video")
        
        ttk.Label(self.video_decode_frame, text="Stego Video:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.stego_video_path = tk.StringVar(value="stego_video.mp4")
        ttk.Entry(self.video_decode_frame, textvariable=self.stego_video_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.video_decode_frame, text="Browse", command=lambda: self.browse_file(self.stego_video_path, [("Video files", "*.mp4;*.avi")])).grid(row=0, column=2, padx=5, pady=5)
        
        # Frame for frame number
        self.frame_number_frame = ttk.Frame(self.video_tab)
        self.frame_number_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(self.frame_number_frame, text="Frame Number:").pack(side=tk.LEFT, padx=5)
        self.frame_number = tk.StringVar(value="1")
        ttk.Entry(self.frame_number_frame, textvariable=self.frame_number, width=10).pack(side=tk.LEFT, padx=5)
        
        # Frame for encryption key
        self.video_key_frame = ttk.Frame(self.video_tab)
        self.video_key_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(self.video_key_frame, text="Encryption Key:").pack(side=tk.LEFT, padx=5)
        self.video_key = tk.StringVar()
        ttk.Entry(self.video_key_frame, textvariable=self.video_key, width=30).pack(side=tk.LEFT, padx=5)
        
        # Frame for message input
        self.video_message_frame = ttk.LabelFrame(self.video_tab, text="Secret Message")
        self.video_message_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.video_message = scrolledtext.ScrolledText(self.video_message_frame, height=10)
        self.video_message.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame for buttons
        button_frame = ttk.Frame(self.video_tab)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Process", command=self.process_video_steganography).pack(side=tk.RIGHT, padx=10)
        
        # Initial mode setup
        self.update_video_mode()
    
    def update_text_mode(self):
        if self.text_mode.get() == "encode":
            self.text_stego_frame.pack_forget()
            self.text_message_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.text_message.config(state=tk.NORMAL)
        else:
            self.text_message.delete(1.0, tk.END)
            self.text_message.config(state=tk.DISABLED)
            self.text_message_frame.pack_forget()
            self.text_stego_frame.pack(fill=tk.X, padx=10, pady=10)
    
    def update_image_mode(self):
        if self.image_mode.get() == "encode":
            self.image_decode_frame.pack_forget()
            self.image_encode_frame.pack(fill=tk.X, padx=10, pady=10)
            self.image_message_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.image_message.config(state=tk.NORMAL)
        else:
            self.image_message.delete(1.0, tk.END)
            self.image_message.config(state=tk.DISABLED)
            self.image_encode_frame.pack_forget()
            self.image_message_frame.pack_forget()
            self.image_decode_frame.pack(fill=tk.X, padx=10, pady=10)
    
    def update_audio_mode(self):
        if self.audio_mode.get() == "encode":
            self.audio_decode_frame.pack_forget()
            self.audio_encode_frame.pack(fill=tk.X, padx=10, pady=10)
            self.audio_message_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.audio_message.config(state=tk.NORMAL)
        else:
            self.audio_message.delete(1.0, tk.END)
            self.audio_message.config(state=tk.DISABLED)
            self.audio_encode_frame.pack_forget()
            self.audio_message_frame.pack_forget()
            self.audio_decode_frame.pack(fill=tk.X, padx=10, pady=10)
    
    def update_video_mode(self):
        if self.video_mode.get() == "encode":
            self.video_decode_frame.pack_forget()
            self.video_encode_frame.pack(fill=tk.X, padx=10, pady=10)
            self.video_message_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.video_message.config(state=tk.NORMAL)
        else:
            self.video_message.delete(1.0, tk.END)
            self.video_message.config(state=tk.DISABLED)
            self.video_encode_frame.pack_forget()
            self.video_message_frame.pack_forget()
            self.video_decode_frame.pack(fill=tk.X, padx=10, pady=10)
    
    def browse_file(self, path_var, file_types):
        filename = filedialog.askopenfilename(filetypes=file_types)
        if filename:
            path_var.set(filename)
    
    def save_file(self, path_var, file_types):
        filename = filedialog.asksaveasfilename(filetypes=file_types)
        if filename:
            path_var.set(filename)
    
    def process_text_steganography(self):
        try:
            if self.text_mode.get() == "encode":
                # Get message from text area
                message = self.text_message.get(1.0, tk.END).strip()
                if not message:
                    messagebox.showerror("Error", "Please enter a message to encode")
                    return
                
                # Prepare variables for encoding
                global file1, file3, nameoffile
                file1 = open(self.cover_text_path.get(), "r+")
                nameoffile = self.text_output_path.get()
                file3 = open(nameoffile, "w+", encoding="utf-8")
                
                # Call the encoding function
                threading.Thread(target=lambda: txt_encode(message)).start()
            else:
                # Set variables for decoding
                global stego
                stego = self.stego_text_path.get()
                
                # Call the decoding function
                threading.Thread(target=decode_txt_data).start()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def process_image_steganography(self):
        try:
            if self.image_mode.get() == "encode":
                # Load the cover image
                image = cv2.imread(self.cover_image_path.get())
                if image is None:
                    messagebox.showerror("Error", "Could not load cover image")
                    return
                
                # Get message and set output path
                global data_to_encode, nameoffile
                data_to_encode = self.image_message.get(1.0, tk.END).strip()
                nameoffile = self.image_output_path.get()
                
                # Call encoding function in separate thread
                threading.Thread(target=lambda: self.run_image_encode(image)).start()
            else:
                # Load stego image for decoding
                image1 = cv2.imread(self.stego_image_path.get())
                if image1 is None:
                    messagebox.showerror("Error", "Could not load stego image")
                    return
                
                # Call decoding function in separate thread
                threading.Thread(target=lambda: decode_img_data(image1)).start()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def run_image_encode(self, image):
        encode_img_data(image)
        messagebox.showinfo("Success", "Image steganography completed successfully")
    
    def process_audio_steganography(self):
        try:
            if self.audio_mode.get() == "encode":
                # Set global variables for audio encoding
                global nameoffile, stegofile
                nameoffile = self.cover_audio_path.get()
                stegofile = self.audio_output_path.get()
                
                # Store the message in a variable accessible to the encoding function
                self.audio_secret_message = self.audio_message.get(1.0, tk.END).strip()
                
                # Call the encoding function in a new thread
                threading.Thread(target=self.run_audio_encode).start()
            else:
                # Set the stego file name for decoding
                global nameoffile_decode
                nameoffile_decode = self.stego_audio_path.get()
                
                # Call the decoding function in a new thread
                threading.Thread(target=decode_aud_data).start()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def run_audio_encode(self):
        # Open wave file
        try:
            song = wave.open(nameoffile, mode='rb')
            
            # Process song as in original code
            nframes = song.getnframes()
            frames = song.readframes(nframes)
            frame_list = list(frames)
            frame_bytes = bytearray(frame_list)
            
            # Use the stored message
            data = self.audio_secret_message
            
            res = ''.join(format(i, '08b') for i in bytearray(data, encoding='utf-8'))
            print("\nThe string after binary conversion :- " + (res))
            length = len(res)
            print("\nLength of binary after conversion :- ", length)
            
            data = data + '*^*^*'
            
            result = []
            for c in data:
                bits = bin(ord(c))[2:].zfill(8)
                result.extend([int(b) for b in bits])
            
            j = 0
            for i in range(0, len(result), 1):
                if j >= len(frame_bytes):
                    break
                    
                res = bin(frame_bytes[j])[2:].zfill(8)
                if i < len(result):
                    if res[len(res)-4] == str(result[i]):
                        frame_bytes[j] = (frame_bytes[j] & 253)  # 253: 11111101
                    else:
                        frame_bytes[j] = (frame_bytes[j] & 253) | 2
                        frame_bytes[j] = (frame_bytes[j] & 254) | result[i]
                j = j + 1
            
            frame_modified = bytes(frame_bytes)
            
            with wave.open(stegofile, 'wb') as fd:
                fd.setparams(song.getparams())
                fd.writeframes(frame_modified)
            print("\nEncoded the data successfully in the audio file.")
            song.close()
            
            messagebox.showinfo("Success", "Audio steganography completed successfully")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during audio encoding: {str(e)}")
    
    def process_video_steganography(self):
        try:
            if self.video_mode.get() == "encode":
                # Store the encryption key
                global encryption_key
                encryption_key = self.video_key.get()
                
                # Store the frame number
                global frame_number_value
                frame_number_value = int(self.frame_number.get())
                
                # Store the message
                global video_secret_message
                video_secret_message = self.video_message.get(1.0, tk.END).strip()
                
                # Store video paths
                global cover_video, stego_video_output
                cover_video = self.cover_video_path.get()
                stego_video_output = self.video_output_path.get()
                
                # Call encoding function
                threading.Thread(target=self.run_video_encode).start()
            else:
                # Set the stego video path and frame number for decoding
                global stego_video_path, stego_frame_number
                stego_video_path = self.stego_video_path.get()
                stego_frame_number = int(self.frame_number.get())
                
                # Set encryption key for decoding
                encryption_key = self.video_key.get()
                
                # Call decoding function
                threading.Thread(target=self.run_video_decode).start()
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def run_video_encode(self):
        try:
            cap = cv2.VideoCapture(cover_video)
            vidcap = cv2.VideoCapture(cover_video)
            
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            frame_width = int(vidcap.get(3))
            frame_height = int(vidcap.get(4))
            
            size = (frame_width, frame_height)
            out = cv2.VideoWriter(stego_video_output, fourcc, 25.0, size)
            
            # Count total frames
            max_frame = 0
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                max_frame += 1
            cap.release()
            print("Total number of Frame in selected Video:", max_frame)
            
            # Check if frame number is valid
            if frame_number_value > max_frame:
                messagebox.showerror("Error", f"Frame number {frame_number_value} exceeds total frames {max_frame}")
                return
                
            # Process frames and embed data
            frame_number = 0
            modified_frame = None
            while vidcap.isOpened():
                frame_number += 1
                ret, frame = vidcap.read()
                if not ret:
                    break
                    
                if frame_number == frame_number_value:
                    # Encrypt the message
                    encrypted_data = encryption(video_secret_message)
                    print("The encrypted data is:", encrypted_data)
                    
                    # Embed data into this frame
                    modified_frame = self.embed_data_in_frame(frame, encrypted_data)
                    frame = modified_frame
                    
                out.write(frame)
            
            vidcap.release()
            out.release()
            
            # Store the modified frame for later decoding
            self.modified_frame = modified_frame
            
            print("\nEncoded the data successfully in the video file.")
            messagebox.showinfo("Success", f"Data successfully encoded in frame {frame_number_value} of the video")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during video encoding: {str(e)}")
    
    def run_video_decode(self):
        try:
            # Open the stego video
            vidcap = cv2.VideoCapture(stego_video_path)
            
            # Check if the video opened successfully
            if not vidcap.isOpened():
                messagebox.showerror("Error", "Could not open the video file")
                return
            
            # Count total frames
            max_frame = 0
            while True:
                ret, _ = vidcap.read()
                if not ret:
                    break
                max_frame += 1
            
            # Check if frame number is valid
            if stego_frame_number > max_frame:
                messagebox.showerror("Error", f"Frame number {stego_frame_number} exceeds total frames {max_frame}")
                return
            
            # Reset video capture to beginning
            vidcap = cv2.VideoCapture(stego_video_path)
            
            # Get to specified frame
            frame_number = 0
            while vidcap.isOpened():
                frame_number += 1
                ret, frame = vidcap.read()
                if not ret:
                    break
                    
                if frame_number == stego_frame_number:
                    # Extract data from frame
                    self.extract_data_from_frame(frame)
                    break
            
            vidcap.release()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during video decoding: {str(e)}")
    
    def embed_data_in_frame(self, frame, data):
        # Implement the embedding logic from the original code
        data = data + '*^*^*'  # Add terminator
        
        binary_data = msgtobinary(data)
        length_data = len(binary_data)
        
        index_data = 0
        
        for i in frame:
            for pixel in i:
                r, g, b = msgtobinary(pixel)
                if index_data < length_data:
                    pixel[0] = int(r[:-1] + binary_data[index_data], 2) 
                    index_data += 1
                if index_data < length_data:
                    pixel[1] = int(g[:-1] + binary_data[index_data], 2) 
                    index_data += 1
                if index_data < length_data:
                    pixel[2] = int(b[:-1] + binary_data[index_data], 2) 
                    index_data += 1
                if index_data >= length_data:
                    break
        return frame
    
    def extract_data_from_frame(self, frame):
        # Implement the extraction logic from the original code
        data_binary = ""
        final_decoded_msg = ""
        for i in frame:
            for pixel in i:
                r, g, b = msgtobinary(pixel) 
                data_binary += r[-1]  
                data_binary += g[-1]  
                data_binary += b[-1]  
                total_bytes = [ data_binary[i: i+8] for i in range(0, len(data_binary), 8) ]
                decoded_data = ""
                for byte in total_bytes:
                    decoded_data += chr(int(byte, 2))
                    if decoded_data[-5:] == "*^*^*": 
                        for i in range(0, len(decoded_data)-5):
                            final_decoded_msg += decoded_data[i]
                        # Decrypt the message using the provided key
                        final_decoded_msg = decryption(final_decoded_msg)
                        print("\n\nThe Encoded data which was hidden in the Video was :--\n", final_decoded_msg)
                        messagebox.showinfo("Decoded Message", final_decoded_msg)
                        return


# Define utility functions from the original code
def txt_encode(text):
    l = len(text)
    i = 0
    add = ''
    while i < l:
        t = ord(text[i])
        if(t >= 32 and t <= 64):
            t1 = t + 48
            t2 = t1 ^ 170  # 170: 10101010
            res = bin(t2)[2:].zfill(8)
            add += "0011" + res
        else:
            t1 = t - 48
            t2 = t1 ^ 170
            res = bin(t2)[2:].zfill(8)
            add += "0110" + res
        i += 1
    res1 = add + "111111111111"
    print("The string after binary conversion applying all the transformation :- " + (res1))
    length = len(res1)
    print("Length of binary after conversion:- ", length)
    HM_SK = ""
    ZWC = {"00": u'\u200C', "01": u'\u202C', "11": u'\u202D', "10": u'\u200E'}
    word = []
    for line in file1:
        word += line.split()
    i = 0
    while(i < len(res1)):
        s = word[int(i/12)]
        j = 0
        x = ""
        HM_SK = ""
        while(j < 12):
            if i+j+1 < len(res1):
                x = res1[j+i] + res1[i+j+1]
                HM_SK += ZWC[x]
                j += 2
            else:
                break
        s1 = s + HM_SK
        file3.write(s1)
        file3.write(" ")
        i += 12
    t = int(len(res1)/12)
    while t < len(word):
        file3.write(word[t])
        file3.write(" ")
        t += 1
    file3.close()
    file1.close()
    print("\nStego file has successfully generated")
    messagebox.showinfo("Success", f"Text steganography completed successfully. Output saved to {nameoffile}")

def decode_txt_data():
    ZWC_reverse = {u'\u200C': "00", u'\u202C': "01", u'\u202D': "11", u'\u200E': "10"}
    file4 = open(stego, "r", encoding="utf-8")
    temp = ''
    for line in file4:
        for words in line.split():
            T1 = words
            binary_extract = ""
            for letter in T1:
                if(letter in ZWC_reverse):
                    binary_extract += ZWC_reverse[letter]
            if binary_extract == "111111111111":
                break
            else:
                temp += binary_extract
    print("\nEncrypted message presented in code bits:", temp)
    lengthd = len(temp)
    print("\nLength of encoded bits:- ", lengthd)
    i = 0
    a = 0
    b = 4
    c = 4
    d = 12
    final = ''
    while i < len(temp):
        if b <= len(temp) and d <= len(temp):
            t3 = temp[a:b]
            a += 12
            b += 12
            i += 12
            t4 = temp[c:d]
            c += 12
            d += 12
            if(t3 == '0110'):
                decimal_data = BinaryToDecimal(t4)
                final += chr((decimal_data ^ 170) + 48)
            elif(t3 == '0011'):
                decimal_data = BinaryToDecimal(t4)
                final += chr((decimal_data ^ 170) - 48)
        else:
            break
    print("\nMessage after decoding from the stego file:- ", final)
    messagebox.showinfo("Decoded Message", final)

def BinaryToDecimal(binary):
    string = int(binary, 2)
    return string

def msgtobinary(msg):
    if type(msg) == str:
        result = ''.join([format(ord(i), "08b") for i in msg])
    elif type(msg) == bytes or type(msg) == np.ndarray:
        result = [format(i, "08b") for i in msg]
    elif type(msg) == int or type(msg) == np.uint8:
        result = format(msg, "08b")
    else:
        raise TypeError("Input type is not supported in this function")
    return result

def encode_img_data(img):
    if (len(data_to_encode) == 0):
        raise ValueError('Data entered to be encoded is empty')

    no_of_bytes = (img.shape[0] * img.shape[1] * 3) // 8

    print("\t\nMaximum bytes to encode in Image :", no_of_bytes)

    if(len(data_to_encode) > no_of_bytes):
        raise ValueError("Insufficient bytes Error, Need Bigger Image or give Less Data !!")

    data = data_to_encode + '*^*^*'

    binary_data = msgtobinary(data)
    print("\n")
    print(binary_data)
    length_data = len(binary_data)

    print("\nThe Length of Binary data", length_data)

    index_data = 0

    for i in img:
        for pixel in i:
            r, g, b = msgtobinary(pixel)
            if index_data < length_data:
                pixel[0] = int(r[:-1] + binary_data[index_data], 2)
                index_data += 1
            if index_data < length_data:
                pixel[1] = int(g[:-1] + binary_data[index_data], 2)
                index_data += 1
            if index_data < length_data:
                pixel[2] = int(b[:-1] + binary_data[index_data], 2)
                index_data += 1
            if index_data >= length_data:
                break
    cv2.imwrite(nameoffile, img)
    print("\nEncoded the data successfully in the Image and the image is successfully saved with name ", nameoffile)

def decode_img_data(img):
    data_binary = ""
    for i in img:
        for pixel in i:
            r, g, b = msgtobinary(pixel)
            data_binary += r[-1]
            data_binary += g[-1]
            data_binary += b[-1]
            total_bytes = [data_binary[i: i+8] for i in range(0, len(data_binary), 8)]
            decoded_data = ""
            for byte in total_bytes:
                decoded_data += chr(int(byte, 2))
                if decoded_data[-5:] == "*^*^*":
                    print("\n\nThe Encoded data which was hidden in the Image was :--  ", decoded_data[:-5])
                    messagebox.showinfo("Decoded Message", decoded_data[:-5])
                    return

def decode_aud_data():
    import wave

    song = wave.open(nameoffile_decode, mode='rb')

    nframes = song.getnframes()
    frames = song.readframes(nframes)
    frame_list = list(frames)
    frame_bytes = bytearray(frame_list)

    extracted = ""
    p = 0
    for i in range(len(frame_bytes)):
        if(p == 1):
            break
        res = bin(frame_bytes[i])[2:].zfill(8)
        if res[len(res)-2] == '0':
            extracted += res[len(res)-4]
        else:
            extracted += res[len(res)-1]

        all_bytes = [extracted[i: i+8] for i in range(0, len(extracted), 8)]
        decoded_data = ""
        for byte in all_bytes:
            if len(byte) == 8:  # Ensure byte is complete
                decoded_data += chr(int(byte, 2))
                if decoded_data[-5:] == "*^*^*":
                    print("The Encoded data was :--", decoded_data[:-5])
                    messagebox.showinfo("Decoded Message", decoded_data[:-5])
                    p = 1
                    break

# Encryption/Decryption functions
def KSA(key):
    key_length = len(key)
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % key_length]) % 256
        S[i], S[j] = S[j], S[i]
    return S

def PRGA(S, n):
    i = 0
    j = 0
    key = []
    while n > 0:
        n = n - 1
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        K = S[(S[i] + S[j]) % 256]
        key.append(K)
    return key

def preparing_key_array(s):
    return [ord(c) for c in s]

def encryption(plaintext):
    key = encryption_key
    key = preparing_key_array(key)

    S = KSA(key)

    keystream = np.array(PRGA(S, len(plaintext)))
    plaintext = np.array([ord(i) for i in plaintext])

    cipher = keystream ^ plaintext
    ctext = ''
    for c in cipher:
        ctext = ctext + chr(c)
    return ctext

def decryption(ciphertext):
    key = encryption_key
    key = preparing_key_array(key)

    S = KSA(key)

    keystream = np.array(PRGA(S, len(ciphertext)))
    ciphertext = np.array([ord(i) for i in ciphertext])

    decoded = keystream ^ ciphertext
    dtext = ''
    for c in decoded:
        dtext = dtext + chr(c)
    return dtext

# Class for redirecting stdout to the GUI console
class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.buffer = ""
        
    def write(self, str):
        self.buffer += str
        self.text_widget.insert(tk.END, str)
        self.text_widget.see(tk.END)
        self.text_widget.update_idletasks()
        
    def flush(self):
        pass

# Main function to run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()