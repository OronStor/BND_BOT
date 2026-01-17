# BND Discord Bot
> A modular and discord bot featuring fun commands , on_event actions , gambling system ,  server monitoring.

## 📝 Description
This project is the final project for **Harvard's CS50P**. 

The **BND Bot** is a discord entertaiment bot with several types of fun and useful functions which you can use 
while hanging out with players!

Key technical challenges addressed in this project include:
* **Asynchronous Programming:** Managing multiple concurrent events and commands.
* **Modular Design:** Utilizing Discord "Cogs" to keep the codebase maintainable.

## 📂 Project Structure

* `project.py`: Entry point. Contains the `main()` function and core utility functions required by the CS50.
* `test_project.py`: Tests for functions in `project.py`.
* `cogs/`: A directory with extensions:
    * `commands.py`: Text user commands (with prefix !).
    * `events.py`: Handles Discord events like member joins and status changes.
    * `gamble.py`: Contains the logic for the casino/gambling system.
    * `notification.py`: Manages automated server notifications.
* `data/`: Local storage for media files and files with users info
* `config.py`: Stores important info (not included in the repository for security).
* `requirements.txt`: Libraries needed to run the project.

P.S: I was foced to rebuild project due to CS50 requirements , u can check main branch to see actual version of bot

## 🛠️ Installation & Usage

### Prerequisites
* Python 3.14
* A Discord token from (https://discord.com/developers/applications).

### Setup
1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/BND_BOT.git](https://github.com/OronStor/BND_BOT.git)
   cd BND_BOT

2. **Depends** 
    pip install -r requirements.txt

3. **Config file**
    Make sure u have config.py in ur root folder with token in it!
    Also u can see some configure files in /data folder, make sure it suits to ur server!

4. **Run bot**
    ```bash
    python project.py

5. **Tests**
    Just run
    ```bash 
    python -m pytest

6. **Commands**
    You can use **!command** to see available commands for bot

