# myJournal
#### Video Demo:  <URL HERE>
#### Description:

**myJournal** is a digital journal application built using Flask. It allows users to write daily journal entries, view their past entries in a calendar view, and track their writing progress with statistics and goals. The app features user authentication (registration, login, and password management) and is designed to help users build and maintain a consistent journaling habit.

This project is currently only available on a local server and was developed as part of a student project.

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Installation and Setup](#installation-and-setup)
4. [Usage](#usage)
5. [Demo](#demo)
6. [Future Improvements](#future-improvements)
7. [License](#license)

## Features

myJournal provides the following features for users:

### Authentication:
- **User Registration**: New users can create an account to begin journaling.
- **Login/Logout**: Users can securely log in and out of their accounts.
- **Change Password**: Users can change their password at any time through their account settings.

### Journal Entry Features:
- **Daily Journal Entry**: Users can create a journal entry for the current day. Only one entry per day is allowed, reinforcing the habit of regular journaling.
- **Past Entries**: A calendar view allows users to navigate through their past entries. Clicking on a specific date redirects users to the entry written on that day.
  
### User Statistics:
- **Total Entries**: Track the total number of journal entries.
- **Total Word Count**: View the cumulative word count of all journal entries.
- **Average Word Count per Entry**: Monitor the average length of entries over time.
- **Current Streak**: See how many consecutive days the user has written an entry.
- **Max Streak**: Track the longest streak of continuous journaling.

### Weekly Goals:
- **Customizable Goals**: Users can set a personal goal for the number of journal entries they wish to write each week.
  
## Tech Stack

myJournal is built using the following technologies:
- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite

## Installation and Setup

To run myJournal locally on your machine, follow these steps:

### Prerequisites
Make sure you have the following installed:
- Python 3.x
- Flask

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd myJournal

# myJournal

**myJournal** is a digital journal application built using Flask. It allows users to write daily journal entries, view their past entries in a calendar view, and track their writing progress with statistics and goals. The app features user authentication (registration, login, and password management) and is designed to help users build and maintain a consistent journaling habit.

This project is currently only available on a local server and was developed as part of a student project.

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Installation and Setup](#installation-and-setup)
4. [Usage](#usage)
5. [Demo](#demo)
6. [Future Improvements](#future-improvements)
7. [License](#license)

## Features

myJournal provides the following features for users:

### Authentication:
- **User Registration**: New users can create an account to begin journaling.
- **Login/Logout**: Users can securely log in and out of their accounts.
- **Change Password**: Users can change their password at any time through their account settings.

### Journal Entry Features:
- **Daily Journal Entry**: Users can create a journal entry for the current day. Only one entry per day is allowed, reinforcing the habit of regular journaling.
- **Past Entries**: A calendar view allows users to navigate through their past entries. Clicking on a specific date redirects users to the entry written on that day.
  
### User Statistics:
- **Total Entries**: Track the total number of journal entries.
- **Total Word Count**: View the cumulative word count of all journal entries.
- **Average Word Count per Entry**: Monitor the average length of entries over time.
- **Current Streak**: See how many consecutive days the user has written an entry.
- **Max Streak**: Track the longest streak of continuous journaling.

### Weekly Goals:
- **Customizable Goals**: Users can set a personal goal for the number of journal entries they wish to write each week.
  
## Tech Stack

myJournal is built using the following technologies:
- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite

## Installation and Setup

To run myJournal locally on your machine, follow these steps:

### Prerequisites
Make sure you have the following installed:
- Python 3.x
- Flask

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd myJournal

### Step 2: Set Up Virtual Environment (Optional but Recommended)
Create and activate a virtual environment to manage dependencies:

```bash
# For Linux/MacOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate

### Step 3: Install Dependencies
Ensure you have a requirements.txt file in the project root and install the dependencies:

```bash
pip install -r requirements.txt

### Step 4: Initialize the Database
Before running the application, you need to set up the SQLite database.

Run the following commands in the Python shell to initialize the database (assuming you have a Flask script that handles the database creation):

```python
from your_flask_app import db
db.create_all()

This will create the necessary tables in your SQLite database.

### Step 5: Run the Application
After setting up the environment, you can run the application locally with the following command:

```bash
flask run

The app will be accessible at http://127.0.0.1:5000/ by default.

## Usage

Once the application is running on your local server, users can:

1. **Register**: Create a new user account by providing a username, email, and password.
   
2. **Login**: Access the app using the registered credentials (username/email and password).
   
3. **Write Entries**: 
   - On the home page, you can write a journal entry for the current day.
   - Only one entry per day is allowed, encouraging consistent journaling.

4. **View Past Entries**: 
   - Navigate through your journal entries using the calendar view.
   - Clicking on a specific date will redirect you to the entry made on that day.

5. **Track Progress**: 
   - Visit the stats page to view key metrics, including:
     - Total number of entries.
     - Cumulative word count.
     - Average word count per entry.
     - Current streak of consecutive entries.
     - Longest streak (max streak) recorded.

6. **Set Weekly Goals**: 
   - Use the journal configuration page to set a personal weekly goal for the number of journal entries you want to complete.
   - This helps you stay motivated and track your weekly journaling habits.


## Future Improvements

Although myJournal is currently a local application, several enhancements could be added in the future:

- **Deployment**: 
  - Deploy the app on a cloud platform like Heroku, AWS, or Azure to make it accessible beyond the local environment.

- **Automated Testing**: 
  - Implement automated tests to improve code quality and ensure the app's stability during updates.

- **Additional Features**:
  - **Tagging and Categorization**: Allow users to tag or categorize journal entries for better organization and retrieval.
  - **Reminders and Notifications**: Add a feature that sends reminders or notifications to encourage users to write daily.
  - **Backup and Export Options**: Integrate options to back up or export journal entries to external platforms (e.g., Google Drive, Dropbox) or file formats (e.g., PDF, CSV).
  - **Dark Mode**: Provide users with an option to switch between light and dark themes for a better user experience.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.
