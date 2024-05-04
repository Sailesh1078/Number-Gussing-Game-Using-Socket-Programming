import socket
import tkinter as tk
from tkinter import messagebox
import threading

# Client configuration
HOST = 'localhost'
PORT = 12345

# Initialize tkinter
root = tk.Tk()
root.title("Game")

# Function to send messages to the server
def send_message():
    message = message_entry.get()
    if message:
        try:
            client_socket.send(message.encode())
            message_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Error sending message: {str(e)}")

# Create GUI elements
message_label = tk.Label(root, text="Enter whatever asked to here:", background='green')
message_label.pack()

message_entry = tk.Entry(root,background='yellow')
message_entry.pack()

send_button = tk.Button(root, text="Send", command=send_message, background='red')
send_button.pack()

# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Create a text widget to display the game messages
game_text = tk.Text(root, height=30, width=80, background='yellow')
game_text.pack()

# Function to handle incoming messages 
def receive_messages():
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break

            # Update the GUI with server messages
            game_text.insert(tk.END, data)
            game_text.see(tk.END)

        except Exception as e:
            messagebox.showerror("Error", f"Error receiving message: {str(e)}")
            break

# Start a thread to handle incoming messages
message_receiver = threading.Thread(target=receive_messages)
message_receiver.start()

root.mainloop()
