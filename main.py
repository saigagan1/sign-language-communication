import tkinter as tk
from tkinter import SOLID
from PIL import Image, ImageTk
import cv2
import numpy as np
import matplotlib.pyplot as plt
import mediapipe as mp
import speech_recognition as sr
import os
import string

# Initialize the main window
win = tk.Tk()
win.title('Sign Language Application')
width = win.winfo_screenwidth()
height = win.winfo_screenheight()
win.geometry(f"{width}x{height}")
win.configure(bg="#FFFFF7")

# Initialize MediaPipe Hands for gesture recognition
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

# Variables and lists
cap = None
upCount = tk.StringVar()
gesture_label = tk.Label(win, textvariable=upCount, font=('Helvetica', 18, 'bold'), bd=5, bg='gray', width=50, fg='#232224', relief=tk.GROOVE)
gesture_label.place(x=400, y=700)

# Alphabet list for sign language
arr = list(string.ascii_lowercase)

# Start camera for gesture detection
def start_camera():
    global cap
    cap = cv2.VideoCapture(0)
    detect_gesture()

# Stop camera and release the video capture
def stop_camera():
    global cap
    if cap:
        cap.release()
        cap = None
        # Clear the video feed
        video_label.config(image='')

def detect_gesture():
    global cap, mpDraw, mpHands, hands, upCount

    if not cap:
        return  # Exit if the camera is off

    # Capture frame from video
    ret, img = cap.read()
    if not ret:
        return

    img = cv2.resize(img, (500, 400))
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    # Gesture recognition logic
    cshow = ''

    if results.multi_hand_landmarks:
        for hand in results.multi_hand_landmarks:
            lm_list = [lm for lm in hand.landmark]
            finger_tips = [8, 12, 16, 20]
            thumb_tip = 4
            finger_fold_status = []

            # Check finger fold status
            for tip in finger_tips:
                if lm_list[tip].x < lm_list[tip - 2].x:
                    finger_fold_status.append(True)
                else:
                    finger_fold_status.append(False)

            # Gesture recognition
            if all(finger_fold_status):  # Check if all fingers are folded
                if lm_list[thumb_tip].y < lm_list[thumb_tip - 1].y < lm_list[thumb_tip - 2].y:
                    cshow = 'I Like it'
                elif lm_list[thumb_tip].y > lm_list[thumb_tip - 1].y > lm_list[thumb_tip - 2].y:
                    cshow = 'I don\'t like it'
            else:
                if lm_list[4].y < lm_list[2].y and lm_list[8].y < lm_list[6].y and lm_list[12].y < lm_list[10].y and \
                        lm_list[16].y < lm_list[14].y and lm_list[20].y < lm_list[18].y and lm_list[17].x < lm_list[
                    0].x < lm_list[5].x:
                    cshow = 'STOP! Don\'t move.'
                elif lm_list[4].y < lm_list[2].y and lm_list[8].y > lm_list[6].y and lm_list[12].y < lm_list[10].y and \
                        lm_list[16].y < lm_list[14].y and lm_list[20].y < lm_list[18].y and lm_list[17].x < lm_list[
                    0].x < lm_list[5].x:
                    cshow = 'Perfect, You did a great job.'
                elif lm_list[4].y < lm_list[2].y and lm_list[8].y < lm_list[6].y and lm_list[12].y > lm_list[10].y and \
                        lm_list[16].y > lm_list[14].y and lm_list[20].y < lm_list[18].y and lm_list[17].x < lm_list[
                    0].x < lm_list[5].x:
                    cshow = 'Good to see you.'
                elif lm_list[8].y < lm_list[6].y and lm_list[12].y > lm_list[10].y and \
                        lm_list[16].y > lm_list[14].y and lm_list[20].y > lm_list[18].y:
                    cshow = 'You Come here.'
                elif lm_list[8].y < lm_list[6].y and lm_list[12].y < lm_list[10].y and \
                        lm_list[16].y > lm_list[14].y and lm_list[20].y > lm_list[18].y:
                    cshow = 'Yes, we won.'
                elif lm_list[4].y < lm_list[2].y and lm_list[8].x < lm_list[6].x and lm_list[12].x > lm_list[10].x and \
                        lm_list[16].x > lm_list[14].x and lm_list[20].x > lm_list[18].x and lm_list[5].x < lm_list[0].x:
                    cshow = 'Move Left'
                elif lm_list[4].y < lm_list[2].y and lm_list[8].x > lm_list[6].x and lm_list[12].x < lm_list[10].x and \
                        lm_list[16].x < lm_list[14].x and lm_list[20].x < lm_list[18].x:
                    cshow = 'Move Right'

            # Display gesture recognition text
            upCount.set(cshow)

            # Draw landmarks on the image
            mpDraw.draw_landmarks(rgb, hand, mpHands.HAND_CONNECTIONS)
            cv2.putText(rgb, cshow, (10, 50), cv2.FONT_HERSHEY_COMPLEX, 0.75, (0, 255, 255), 2)

    # Update video feed for Tkinter
    image = Image.fromarray(rgb)
    finalImage = ImageTk.PhotoImage(image)
    video_label.configure(image=finalImage)
    video_label.image = finalImage
    win.after(1, detect_gesture)

# Initialize speech recognition for audio to alphabetical sign language
def audio_to_sign():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        try:
            print("Listening...")
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio).lower()
            print("You said:", text)

            # Show all letters in the spoken text at once
            show_phrase(text)
        except Exception as e:
            print("Error:", str(e))

# Close the output display window for audio output
def close_output():
    plt.close('all')  # Close all matplotlib windows

def show_phrase(phrase):
    # Filter out only valid letters and corresponding images
    images = [f'letters/{char}.jpg' for char in phrase if char in arr and os.path.exists(f'letters/{char}.jpg')]
    
    if images:
        fig, axes = plt.subplots(1, len(images), figsize=(len(images) * 2, 2))
        if len(images) == 1:  # If only one image, make axes iterable
            axes = [axes]

        for ax, img_path in zip(axes, images):
            img = Image.open(img_path)
            ax.imshow(np.array(img))
            ax.axis('off')  # Hide axes for cleaner look

        plt.show(block=False)  # Non-blocking display
        plt.pause(3)  # Show the images for a few seconds
        # plt.close() is now controlled by the close_output button

# Create and pack the video and control widgets
video_label = tk.Label(win, width=500, height=400, bg="#FFFFF7")
video_label.place(x=40, y=200)

# Buttons
start_button = tk.Button(win, text="Start Camera for Gesture Recognition", font=('Helvetica', 16), bg='blue', fg='white', command=start_camera)
start_button.pack(pady=5)

stop_button = tk.Button(win, text="Stop Camera", font=('Helvetica', 16), bg='red', fg='white', command=stop_camera)
stop_button.pack(pady=5)

audio_button = tk.Button(win, text="Audio to Alphabet Sign Language", font=('Helvetica', 16), bg='green', fg='white', command=audio_to_sign)
audio_button.pack(pady=5)

close_output_button = tk.Button(win, text="Close Output", font=('Helvetica', 16), bg='orange', fg='white', command=close_output)
close_output_button.pack(pady=5)

# Load and display the provided sign language image below the buttons
sign_image_path = 'signlang.png'  # Ensure the image is in the same directory
sign_image = Image.open(sign_image_path)
sign_image = sign_image.resize((300, 150), Image.LANCZOS)
sign_photo = ImageTk.PhotoImage(sign_image)

# Center the image below the buttons
image_x_position = (width - 300) // 2  # Center the image horizontally
sign_image_label = tk.Label(win, image=sign_photo, bg="#FFFFF7")
sign_image_label.place(x=image_x_position, y=250)  # Position below buttons

# Start Tkinter main loop
win.mainloop()
