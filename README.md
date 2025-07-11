# Twidder

## Project Overview

Twidder is a minimalist web-based social media application that allows users to sign up, sign in, post messages, and interact with other users' profiles. Built as a full-stack solution, it emphasizes secure user authentication, real-time session management, and a clean user interface for a seamless microblogging experience.

## Features

* **User Authentication & Authorization**:
    * **Secure Sign-Up**: Users can create new accounts with robust password hashing using `Flask-Bcrypt`.
    * **Secure Sign-In**: Authenticated access with a session token generated upon successful login.
    * **HMAC-Based Security**: All API requests (except public ones like sign-in/sign-up) are secured with HMAC-SHA256 signatures, ensuring data integrity and authenticity using a user-specific token and timestamp.
* **Profile Management**:
    * **Personalized Home Page**: Displays the logged-in user's information and message wall.
    * **Password Change**: Securely change account passwords.
* **Messaging Functionality**:
    * **Post Messages**: Users can post messages to their own wall or to the wall of another user.
    * **Message Wall**: View all messages posted to a user's wall.
    * **Drag-and-Drop Message Feature**: An interactive element on the home page allowing users to drag messages.
* **User Browse**:
    * **Search Users**: Find other users by their email address.
    * **View Other Profiles**: Access another user's public information and their message wall.
* **Real-time Session Management**:
    * **WebSockets Integration**: Utilizes WebSockets (`Flask-Sock`) to manage user sessions across multiple browser tabs or devices, enforcing a single active session by logging out older connections upon a new login.
    * **Secure WebSocket Handshake**: WebSocket connections are authenticated using HMAC signatures based on the user's token and timestamp.
* **Error Handling**: Comprehensive client-side and server-side error messages provide clear feedback to the user based on specific status codes and predefined message mappings.

## Technologies Used

### Backend (Python - Flask)
* **Flask**: A lightweight Python web framework for building the RESTful API.
* **Flask-Sock**: Extends Flask to enable WebSocket communication for real-time features.
* **Flask-Bcrypt**: Provides robust password hashing and checking functionalities.
* **SQLite3**: Used as the relational database for storing user data and messages (`database.db`).
* **HMAC**: Cryptographic hashing for request signature verification, ensuring secure API communication.
* **`random` & `math`**: Used for secure token generation.
* **`re` (Regular Expressions)**: For email format validation.

### Frontend (HTML, CSS, JavaScript)
* **HTML5**: Structures the web application, leveraging `script type="text/template"` for dynamic view rendering.
* **CSS3**: Styles the application, providing a clean and organized user interface.
* **JavaScript (Vanilla JS)**: Handles all client-side logic, including:
    * AJAX requests (`XMLHttpRequest`) for interacting with the backend API.
    * Dynamic content rendering based on user authentication status (`updateView`).
    * Form validation and submission.
    * WebSocket client implementation for real-time logout.
    * **`CryptoJS`**: Client-side library used to generate HMAC signatures for secure API requests and WebSocket connections.

### Database
* **SQLite3**: A file-based SQL database used to store user information (firstname, familyname, email, hashed password, gender, city, country, token) and messages (writer\_id, receiver\_id, content). The `database_helper.py` module manages all database interactions.

## Installation and Setup

To get Twidder up and running on your local machine, follow these steps:

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/diastoff1/Twidder.git](https://github.com/diastoff1/Twidder.git)
    cd Twidder
    ```

2.  **Set up a Python Virtual Environment (Recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    It's assumed your `requirements.txt` would contain:
    ```
    Flask
    Flask-Sock
    Flask-Bcrypt
    ```
    Install them using:
    ```bash
    pip install Flask Flask-Sock Flask-Bcrypt
    ```

4.  **Initialize the Database:**
    The project uses an SQLite database. You'll need to create the `database.db` file and set up the schema. Based on `database_helper.py`, you'd typically have a `schema.sql` file (which wasn't provided, but is crucial for initial setup) and a way to run it.
    * **Create `database.db`**: An empty `database.db` file will be created when `sqlite3.connect(DATABASE_URI)` is first called.
    * **Populate Schema**: You would typically run the SQL commands from `schema.sql` to create the `users` and `messages` tables. (You might need to create a `schema.sql` file if you don't have one and manually run it against `database.db`.)

    Example `schema.sql` (inferred from `database_helper.py` comments and queries):
    ```sql
    DROP TABLE IF EXISTS messages;
    DROP TABLE IF EXISTS users;

    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        firstname VARCHAR(120) NOT NULL,
        familyname VARCHAR(120) NOT NULL,
        email VARCHAR(120) NOT NULL UNIQUE,
        password VARCHAR(120) NOT NULL,
        gender VARCHAR(120) NOT NULL,
        city VARCHAR(120) NOT NULL,
        country VARCHAR(120) NOT NULL,
        token VARCHAR(36)
    );

    CREATE TABLE messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        writer_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        FOREIGN KEY (writer_id) REFERENCES users(id),
        FOREIGN KEY (receiver_id) REFERENCES users(id)
    );
    ```
    You would typically run this using a Python script or `sqlite3` command line:
    ```bash
    sqlite3 database.db < schema.sql
    ```

5.  **Run the Flask Application:**
    ```bash
    python server.py
    ```
    The application will typically run on `http://127.0.0.1:5000/`.

## Usage

1.  **Access the Application**: Open your web browser and navigate to `http://127.0.0.1:5000/`.
2.  **Sign Up**: Create a new account using the provided sign-up form. Ensure your password is at least 8 characters long.
3.  **Sign In**: Log in with your registered email and password.
4.  **Home Tab**:
    * View your personal information.
    * Load and view messages posted on your wall.
    * Post a new message (it will post to your own wall by default, as inferred from `postMessage` client-side logic).
    * Drag messages from your wall to the "status box".
5.  **Browse Tab**:
    * Search for other users by their email.
    * View their public profile information.
    * View their message wall.
    * Post a message directly to another user's wall.
6.  **Account Tab**:
    * Change your password.
    * Sign out of your account. Note that signing out (or signing in from another location) will log out other active sessions for the same user due to WebSocket integration.
