import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
import quiz_backend  # Import the backend module
from tkinter import messagebox  # Import the messagebox for displaying alerts

# Initialize progress for each intensity level
progress = {intensity: {"score": 0, "completed": False} for intensity in quiz_backend.intensity_data.keys()}

# Dictionary to store user scores for each intensity
user_scores = {intensity: 0 for intensity in quiz_backend.intensity_data.keys()}

selected_intensity = None  # Initialize the selected intensity variable

def show_intensity_selection():
    # This function is called when the user clicks the "Start Quiz" button after entering their name.
    name = name_entry.get()
    if name:
        # If the user has entered a name, hide the name frame and show the intensity selection frame.
        name_frame.pack_forget()
        intensity_frame.pack()
    else:
        # If no name is entered, display a warning message.
        messagebox.showwarning("Name Required", "Please enter your name.")

def start_quiz():
    global selected_intensity  # Declare selected_intensity as global
    # This function is called when the user clicks the "Start Quiz" button after selecting an intensity.
    selected_intensity = intensity_var.get()

    if progress[selected_intensity]["completed"]:
        # If the selected intensity is already completed, show a message and reset the intensity selection.
        messagebox.showinfo("Intensity Completed", f"You have completed all items for {selected_intensity} intensity.")
        intensity_var.set("new_intensity")
        return

    if quiz_backend.start_quiz(selected_intensity):
        # If the quiz for the selected intensity can be started, initiate the questionnaire.
        start_questionnaire(selected_intensity)
    else:
        # If the quiz for the selected intensity is already finished, display a warning message.
        messagebox.showwarning("Intensity is already finished", "Please select another intensity.")

def start_questionnaire(intensity):
    # This function initiates the quiz questionnaire for the selected intensity.
    global current_question, score, current_questions, selected_intensity  # Declare selected_intensity as global
    current_question = 0
    score = 0
    current_questions = quiz_backend.intensity_data[intensity]

    # Hide the intensity selection frame.
    intensity_frame.pack_forget()

    # Show the quiz interface elements.
    qs_label.pack()
    for button in choice_btns:
        button.pack()
    feedback_label.pack()
    next_btn.pack()

    # Set the selected intensity variable
    selected_intensity = intensity

    show_question()

def display_completion_message(intensity):
    score = progress[intensity]["score"]
    total_questions = len(quiz_backend.intensity_data[intensity])
    message = f"You completed {intensity}, Your score is {score}/{total_questions}"

    # Use after to schedule the messagebox.showinfo after the GUI has updated
    root.after(1, lambda: messagebox.showinfo(f"{intensity} Quiz Completed", message))

    # Optionally, you can include any other actions you want to perform after showing the messagebox.

def show_question():
    global current_question, selected_intensity

    if current_question < len(current_questions):
        question = current_questions[current_question]

        question_text = question["question"]
        qs_label.config(text=question_text)

        choices = question["choices"]
        for i in range(4):
            choice_btns[i].config(text=choices[i], state="normal", command=lambda i=i: check_answer(i))

        feedback_label.config(text="")
        next_btn.config(state="disabled")

    else:
        # If all questions are answered, display the final score and update progress.
        # Reset the quiz or perform any other actions as needed
        reset_quiz()

        # Update progress for the current intensity
        progress[selected_intensity]["score"] = score
        progress[selected_intensity]["completed"] = True

        # Update the user's score for the completed intensity
        user_scores[selected_intensity] += score  # Fix: Add the score instead of setting it to the current score

        # Display completion message after resetting the quiz
        display_completion_message(selected_intensity)

        return  # Stop execution here to avoid calling show_question() again

    # Increment the question counter only when the user clicks the "Next" button
    current_question += 1

def check_answer(choice):
    # This function checks if the selected choice matches the correct answer.
    selected_choice = choice_btns[choice]["text"]
    correct_answer = current_questions[current_question - 1]["answer"]

    if quiz_backend.check_answer(selected_choice, correct_answer):
        global score
        score += 1
        feedback_label.config(text="Correct!", foreground="green")
    else:
        feedback_label.config(text="Incorrect!", foreground="red")

    for button in choice_btns:
        button.config(state="disabled")
    next_btn.config(state="normal")

    if current_question == len(current_questions):
        reset_quiz()

def reset_quiz():
    # This function resets the quiz state, hides the quiz interface, and shows the intensity selection frame.
    global user_scores
    # Update the user's score for the completed intensity
    user_scores[selected_intensity] += score

    for button in choice_btns:
        button.config(state="disabled")
        button.pack_forget()
    feedback_label.pack_forget()
    next_btn.pack_forget()
    qs_label.pack_forget()
    intensity_frame.pack()

    # Check if the intensity is completed after packing the intensity_frame
    if progress[selected_intensity]["completed"]:
        # Display completion message after resetting the quiz
        display_completion_message(selected_intensity)

# Add this line at the beginning to initialize user_scores
user_scores = {intensity: 0 for intensity in quiz_backend.intensity_data.keys()}

def check_score():
    # This function displays the user's scores for each intensity.
    completed_intensities = [intensity for intensity, data in progress.items() if data["completed"]]
    
    if len(completed_intensities) == len(quiz_backend.intensity_data):
        # If all intensities are completed, show a congratulatory message.
        messagebox.showinfo("Congratulations!", "You have finished the quiz. You may check your scores.")
    else:
        # If not all intensities are completed, display the user's scores for each intensity.
        score_message = "\n".join([f"{intensity}: {user_scores.get(intensity, 'Not completed')}" for intensity in quiz_backend.intensity_data.keys()])
        messagebox.showinfo("Your Score", score_message)

root = tk.Tk()
root.title("ProgQuiz")
root.geometry("800x550")
style = Style(theme="flatly")

# Create a frame for entering the name
name_frame = ttk.Frame(root)
name_frame.pack()

name_label = ttk.Label(name_frame, text="Enter Your Name:")
name_label.pack(pady=10)

name_entry = ttk.Entry(name_frame)
name_entry.pack(pady=10)

name_button = ttk.Button(name_frame, text="Start Quiz", command=show_intensity_selection)
name_button.pack(pady=20, padx=20)

# Create a frame for selecting quiz intensity
intensity_frame = ttk.Frame(root)
intensity_frame.pack_forget()

intensity_label = ttk.Label(intensity_frame, text="Select Quiz Intensity:")
intensity_label.pack()

intensity_var = tk.StringVar()
intensity_var.set("new_intensity")

# Create intensity selection radio buttons
for option in quiz_backend.intensity_data.keys():
    intensity_button = ttk.Radiobutton(intensity_frame, text=option, variable=intensity_var, value=option)
    intensity_button.pack(pady=5)

start_button = ttk.Button(intensity_frame, text="Start Quiz", command=start_quiz)
start_button.pack(pady=10)

# Button to check user's scores
check_score_button = ttk.Button(intensity_frame, text="Check Score", command=check_score)
check_score_button.pack(pady=10)

# Initialize variables
current_question = 0
score = 0
current_questions = []
intensity_options = list(quiz_backend.intensity_data.keys())

# Create labels, buttons, and other UI elements for the quiz interface
qs_label = ttk.Label(root, anchor="center", wraplength=500, padding=10)
qs_label.pack(pady=10)
qs_label.pack_forget()

choice_btns = []
for i in range(4):
    button = ttk.Button(root, command=lambda i=i: check_answer(i))
    button.pack(pady=5)
    choice_btns.append(button)
    button.pack_forget()

feedback_label = ttk.Label(root, anchor="center", padding=10)
feedback_label.pack()
feedback_label.pack_forget()

next_btn = ttk.Button(root, text="Next", command=show_question, state="disabled")
next_btn.pack(padx=10)
next_btn.pack_forget()

root.iconbitmap("pyt.ico")
style.configure("TLabel", font=("Helvetica", 20))
style.configure("TButton", font=("Helvetica", 16))
style.configure("TRadiobutton", font=("Helvetica", 20))
style.configure("TButton", font=("Helvetica", 20))

# Start the main application loop
root.mainloop()
