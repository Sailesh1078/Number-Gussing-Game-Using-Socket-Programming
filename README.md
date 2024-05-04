# Number Guessing Game with Client-Server Architecture

This repository hosts a client-server application for a number guessing game, employing Python's socket programming for network communication. The game allows multiple clients to connect concurrently to a central server, participate in a number guessing challenge, and manage authentication, gameplay, and session persistence.

## Technical Overview

- **Client-Server Communication**: The game relies on TCP/IP socket communication for exchanging data between the clients and the server. The server listens on a predefined port for incoming connections and manages client requests.

- **Authentication Mechanism**: To access the game, clients are required to provide a username and password, which are authenticated against a predefined set of credentials stored on the server.

- **Game Logic**: Once authenticated, clients engage in a number guessing game where they attempt to guess a randomly generated number between 1 and 100. The server provides feedback based on the client's guess, indicating whether it is higher or lower than the target number.

- **Concurrency Handling**: The server supports concurrent gameplay for multiple clients using threading. It employs a semaphore to limit the number of simultaneous players, ensuring fairness and optimal resource utilization.

- **Data Persistence**: Player information, including login history, session details, and game scores, is persisted in text files (`attemptsleft.txt`, `loginandattempt.txt`, and `scores.txt`, respectively). These files store crucial data for tracking player activity and facilitating future analysis.

- **Payment System Integration**: The application features a rudimentary payment system for extending the number of game sessions. Clients who exhaust their allocated attempts can opt to make a payment to continue playing, with various payment models available.

## File Structure

- **client.py**: Implements the client-side logic of the game using Python's Tkinter library for the graphical user interface (GUI).
- **server.py**: Contains the server-side implementation, managing client connections, authentication, gameplay, and data persistence.
- **attemptsleft.txt**: Stores the remaining attempts for each player, facilitating session management.
- **loginandattempt.txt**: Records login history and sessions played by each player for auditing purposes.
- **scores.txt**: Logs game scores, including player names, attempts, and time taken, for performance analysis and leaderboard generation.

## Dependencies

- **Python 3.12**: The core programming language used for scripting the client and server applications.
- **Tkinter**: Required for creating the graphical user interface in the client application.

## Contribution Guidelines

Contributions to the project are welcome! If you encounter bugs, have feature requests, or wish to contribute enhancements, please feel free to submit issues or pull requests. Your contributions will help improve the overall quality and functionality of the game.
