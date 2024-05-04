import socket
import threading
import random
import time
import uuid

# Server configuration
HOST = 'localhost'
PORT = 12345
file_path = "attemptsleft.txt"

# Dictionary to store client names and keys (passwords)
client_credentials = {
    "user1": "password1",
    "user2": "password2",
    "user3": "password3"
}

# Dictionary to store client connections and their game information
clients = {}

# List to store the top 5 earliest guesses based on time taken
top_5_earliest_guesses = []

# Semaphore to limit the number of concurrent players
game_semaphore = threading.Semaphore(3)

# Function to handle client connections
def handle_client(client_socket,attempts_dict):
    try:
        # Receive and store the client's name and key (password)
        client_socket.send("Enter your name:\n".encode())
        client_name = client_socket.recv(1024).decode()
        client_socket.send("Enter your key (password):\n".encode())
        client_key = client_socket.recv(1024).decode()
        print(f"New connection from {client_name}")

        # Authenticate the client based on their name and key
        if authenticate_client(client_name, client_key):
            clients[client_name] = {"socket": client_socket}

            # Generate a unique identifier (not actual MAC address)
            client_uuid = uuid.uuid4().hex

            # Send the unique identifier to the client
            client_socket.send(f"Your unique identifier: {client_uuid}\n".encode())
            
            attempts_left= get_attempts_left(attempts_dict, client_name,client_key)
            client_socket.send(f"Number of Sessions left: {attempts_left}\n".encode())
            if (int(attempts_left)>0):
                # Send welcome message and game instructions
                client_socket.send("Number Guessing Game begins\n".encode())
                client_socket.send("Guess a number between 1 and 100.\n".encode())

                # Acquire the semaphore to limit the number of concurrent players
                with game_semaphore:
                    sessions = 0
                    while True:
                        # Generate a random number for the game
                        secret_number = random.randint(1, 100)
                        print(f"The next secret number for {client_name} is {secret_number}")
                        attempts = 0
                        sessions+=1
                        attempts_left= get_attempts_left(attempts_dict, client_name,client_key)
                        new_attempts=int(attempts_left)-1
                        update_and_get_attempts_left(attempts_dict, client_name, client_key, new_attempts)
                        start_time = time.time()

                        while True:
                            client_socket.send("Enter your guess:\n".encode())
                            guess = int(client_socket.recv(1024).decode())
                            attempts += 1

                            if guess == secret_number:
                                end_time = time.time()
                                time_taken = end_time - start_time
                                clients[client_name]["time"] = time_taken
                                client_socket.send(f"Congratulations! You guessed it in {attempts} attempts in {time_taken:.2f} seconds.\n".encode())

                                # Store the game result in scores.txt with unique identifier and client name
                                with open("scores.txt", "a") as scores_file:
                                    scores_file.write(f"Player: {client_name}, Key: {client_key}, MAC Address: {client_uuid}, Attempts: {attempts}, Time: {time_taken:.2f} seconds\n")
                                
                                
                                # Update the top 5 earliest guesses list
                                update_top_5_earliest_guesses(client_name, attempts, time_taken)
                                # print(top_5_earliest_guesses)
                                if {'Player': client_name, 'Attempts': attempts, 'Time': time_taken} in top_5_earliest_guesses:
                                    client_socket.send("Congratulations Your attempt is in Top 5.\n".encode())
                                    print(new_attempts)
                                    attempts_left= get_attempts_left(attempts_dict, client_name,client_key)
                                    new_attempts=int(attempts_left)+1
                                    update_and_get_attempts_left(attempts_dict, client_name, client_key, new_attempts)
                                    client_socket.send('For your exceptional performance,you are awarded 1 FREE SESSION.\n'.encode())
                                else:
                                    client_socket.send("Not in Top 5.\n".encode())
                                break
                            elif (guess+10) > secret_number and guess < secret_number:
                                client_socket.send("[YOU ARE CLOSE]Try little higher.\n".encode())
                            
                            elif (guess-10) < secret_number and guess > secret_number:
                                client_socket.send("[YOU ARE CLOSE]Try little lower.\n".encode())
                                
                            elif (guess+10) < secret_number and guess < secret_number:
                                client_socket.send("Try higher.\n".encode())
                            else:
                                client_socket.send("Try lower.\n".encode())
                        
                        attempts_left= get_attempts_left(attempts_dict, client_name,client_key)
                        print(f"The number of sessions left now{attempts_left}")
                        if (int(attempts_left)>0):
                            play_again = client_socket.recv(1024).decode()
                            if play_again.lower() != "yes" and play_again.lower() != "lhist" and play_again.lower()!="ahist":
                                with open("loginandattempt.txt", "a") as scores_file:
                                    scores_file.write(f"Player: {client_name}, Key: {client_key}, MAC Address: {client_uuid}, Sessions Played: {sessions}\n")
                                break
                                
                            elif play_again.lower() == "lhist":
                                # Call the function to extract player information
                                player_info = extract_player_info("loginandattempt.txt", client_name, client_key)

                                # Print the extracted information
                                if player_info:
                                    client_socket.send(f"[LOGIN HISTORY] Player: {client_name}\n".encode())
                                    for info in player_info:
                                        client_socket.send(f"MAC Address: {info['MAC Address']}, Sessions Played: {info['Sessions Played']}\n".encode())
                                else:
                                    print("Player not found or invalid credentials.")
                                break
                            
                            elif play_again.lower() == "ahist":
                                # Function to extract player information from the text file
                                def extract_player_info2(file_path, player_name, player_key):
                                    player_info = []

                                    with open(file_path, 'r') as file:
                                        for line in file:
                                            if f"Player: {player_name}, Key: {player_key}" in line:
                                                player_info.append(line.strip())

                                    return player_info

                                # Specify the path to the text file
                                file_path = "scores.txt"

                                # Extract player information
                                player_info = extract_player_info2(file_path, client_name, client_key)

                                # Check if any information was found
                                if player_info:
                                    client_socket.send(f"Information for {client_name} with key {client_key}:\n".encode())
                                    for info in player_info:
                                        client_socket.send(f"Player_Name: {info['Player']}, Player_Key: {info['Key']},MAC Address: {info['MAC Address']}, Attempts: {info['Attempts']}, Time: {info['Time']}\n".encode())
                                else:
                                    print(f"No information found for {client_name} with key {client_key}.")

                            
                        else:
                            client_socket.send("OOPS seems like you are out of attempts.\n".encode())
                            client_socket.send("You need To pay inorder to Continue Playing.\n".encode())
                            client_socket.send("Payment Models- \n1. 25Rupees per session\n2. 500Rupees for 25 sessions.\n3.15 Rupees per sessions(If Payment>500)\nMinimum Recharge balance- Rs50\n".encode())
                            payment = client_socket.recv(1024).decode()
                            l = []
                            print(l)
                            l = payment.split()
                            l[1] = int(l[1])
                            print()
                            
                            if (l[1]>=50):
                                attempts_left= get_attempts_left(attempts_dict, client_name,client_key)
                                new_attempts=int(attempts_left)+(l[1]//25)
                                update_and_get_attempts_left(attempts_dict, client_name, client_key, new_attempts)
                                break
                                
                            elif (l[1]>500):
                                attempts_left= get_attempts_left(attempts_dict, client_name,client_key)
                                new_attempts=int(attempts_left)+(l[1]//15)
                                update_and_get_attempts_left(attempts_dict, client_name, client_key, new_attempts)
                                break
                                
                            elif(l[1]==500):
                                attempts_left= get_attempts_left(attempts_dict, client_name,client_key)
                                new_attempts=int(attempts_left)+25
                                update_and_get_attempts_left(attempts_dict, client_name, client_key, new_attempts)
                                break
                                
                
            else: 
                client_socket.send("OOPS seems like you are out of attempts.\n".encode())
                client_socket.send("You need To pay inorder to Continue Playing.\n".encode())
                client_socket.send("Payment Models- \n1. 25Rupees per session\n2. 500Rupees for 25 sessions.\n3.15 Rupees per sessions(If Payment>500)\nMinimum Recharge balance- Rs50\n".encode())
                payment = client_socket.recv(1024).decode()
                l = []
                print(l)
                l = payment.split()
                l[1] = int(l[1])
                print()
                
                if (l[1]>=50):
                    attempts_left= get_attempts_left(attempts_dict, client_name,client_key)
                    new_attempts=int(attempts_left)+(l[1]//25)
                    update_and_get_attempts_left(attempts_dict, client_name, client_key, new_attempts)
                    
                elif (l[1]>500):
                                attempts_left= get_attempts_left(attempts_dict, client_name,client_key)
                                new_attempts=int(attempts_left)+(l[1]//15)
                                update_and_get_attempts_left(attempts_dict, client_name, client_key, new_attempts)
                    
                elif(l[1]==500):
                    attempts_left= get_attempts_left(attempts_dict, client_name,client_key)
                    new_attempts=int(attempts_left)+25
                    update_and_get_attempts_left(attempts_dict, client_name, client_key, new_attempts)
                
                    

        else:
            client_socket.send("Authentication failed. Disconnected.\n".encode())

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        client_socket.close()
        del clients[client_name]
        print(f"{client_name} disconnected.")

# Function to authenticate clients based on their name and key (password)
def authenticate_client(client_name, client_key):
    return client_credentials.get(client_name) == client_key

def update_top_5_earliest_guesses(client_name, attempts, time_taken):
    global top_5_earliest_guesses
    top_5_earliest_guesses.append({"Player": client_name, "Attempts": attempts, "Time": time_taken})
    top_5_earliest_guesses = sorted(top_5_earliest_guesses, key=lambda x: x["Time"])[:5]
    notify_clients_top_5()

# Function to notify all clients about the updated top 5 list
def notify_clients_top_5():
    top_5_message = "\nTop 5 Earliest Guesses:\n"
    for idx, entry in enumerate(top_5_earliest_guesses, start=1):
        top_5_message += f"{idx}. Player: {entry['Player']}, Attempts: {entry['Attempts']}, Time: {entry['Time']:.2f} seconds\n"
    
    # Send the top 5 list to all connected clients
    for client_name, client_info in clients.items():
        client_socket = client_info["socket"]
        client_socket.send(top_5_message.encode())
    
def update_attempts_file(file_path, attempts_dict):
    with open(file_path, 'w') as file:
        for player_info in attempts_dict.values():
            file.write(f"Player: {player_info['Player']}, Key: {player_info['Key']}, Attempts_Left: {player_info['Attempts_Left']}\n")
        
def update_and_get_attempts_left(attempts_dict, player_name, key, new_attempts):
    if player_name in attempts_dict and attempts_dict[player_name]['Key'] == key:
        attempts_dict[player_name]['Attempts_Left'] = new_attempts
        update_attempts_file(file_path, attempts_dict)
        print(f'Updated Attempts Left for {player_name}: {new_attempts}')
    else:
        print('Invalid credentials')        

def extract_player_info(filename, player_name, player_key):
    player_info = []

    with open(filename, 'r') as file:
        lines = file.readlines()

        for line in lines:
            # Split each line into parts based on commas and spaces
            parts = line.strip().split(', ')

            # Initialize variables to store player information
            found_name = None
            found_key = None
            mac_address = None
            sessions_played = None

            # print(f"{player_name} - {player_key}")
            # Extract information from parts
            for part in parts:
                key, value = part.strip().split(': ')
                if key == "Player":
                    found_name = value
                    #print(found_name)
                elif key == "Key":
                    found_key = value
                   # print(found_key)
                elif key == "MAC Address":
                    mac_address = value
                   # print(mac_address)
                elif key == "Sessions Played":
                    sessions_played = value
                   # print(sessions_played)

            # Check if the extracted information matches the user inputu            
            if found_name == player_name and found_key == player_key:
                player_info.append({
                    "MAC Address": mac_address,
                    "Sessions Played": sessions_played
                })

    return player_info

def read_attempts_file(file_path):
    attempts_dict = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.strip():
                parts = line.strip().split(',')
                player_info = {}
                for part in parts:
                    key, value = part.strip().split(': ')
                    player_info[key] = value
                player_name = player_info['Player']
                attempts_dict[player_name] = player_info
    return attempts_dict

def get_attempts_left(attempts_dict, player_name, key):
    if player_name in attempts_dict and attempts_dict[player_name]['Key'] == key:
        attempts_left = attempts_dict[player_name]['Attempts_Left']
        return(attempts_left)
    else:
        exit(1)

# Main server loop
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Server listening on {HOST}:{PORT}")
    attempts_dict = read_attempts_file(file_path)

    while True:
        client_socket, addr = server.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket,attempts_dict,))
        client_handler.start()

if __name__ == "__main__":
    main()
