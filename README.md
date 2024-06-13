# Project Overview
![admin_view](https://github.com/Oduo24/Savings-Loan-and-Investment-App/assets/82431848/4c3e7b3e-85e4-43f3-afbf-da526692557f)

This project is a web-based savings, loan, and investment platform designed to help users manage their finances. Built using Flask, MySQL (SQLAlchemy), Bootstrap, and other JavaScript libraries, the platform offers a user-friendly interface for saving money, applying for loans, and making investments. It has two different user roles(admin and normal user). Users can deposit savings, request loans, and track their investment performance, all through a secure and intuitive web application. The platform also includes features for managing transactions, calculating interest, and providing financial reports.

## 1. Project Structure
1. models/ - 
Contains the SQLAlchemy models defining the database schema for the platform. Each model represents a table in the database
2. static/ - 
Holds static files such as CSS, JavaScript, and images. This directory is served directly to the client and helps in styling and enhancing the user interface of the platform.
3. templates/ - 
Includes HTML templates used by Flask to render web pages. These templates are rendered with dynamic data from the server and provide the structure and layout for the web pages of the application.
4. utility/ - 
Contains utility scripts and helper functions that support various operations within the platform. This can include data validation, formatting, and other reusable code snippets that assist in the smooth functioning of the application.
5. app.py - 
The main entry point of the application. This file initializes the Flask app, sets up routes, and handles the request/response cycle. It integrates the different components of the platform and starts the web server.
6. db_storage.py - 
Manages database connections and operations. This script sets up SQLAlchemy to interface with the MySQL database, handling tasks such as creating tables, querying, and committing changes to the database.
7. jobs.py - 
Schedules and runs background tasks and jobs. This can include tasks such as processing transactions, sending notifications, and performing periodic maintenance activities necessary for the platform's operation.
## 2. Installation
### Clone the repo
```
git clone https://github.com/Oduo24/Savings-Loan-and-Investment-App
cd Savings-Loan-and-Investment-App
```
### Create a Virtual Environment
```
python3 -m venv venv
source venv/bin/activate
```
### Install Dependencies
```
pip install -r requirements.txt
```
### Run application
```
python3 app.py
```
The application will be available at http://127.0.0.1:5000.

## 3. Usage
1. The admin can perform the following roles
- Add new users.
- Make receipts.
- Disburse approved loans.
- Surcharge a user account.
- Generate reports like P&L trial balance and Balance Sheet.
- Change account settings.

![making-a-payment](https://github.com/Oduo24/Savings-Loan-and-Investment-App/assets/82431848/2655d4df-3dfc-4b4d-8001-b960f19efb31)

2. A normal user can perform the following roles
- View his account balance summaries like savings, outstanding loan balance and fines.
  ![user-home-page](https://github.com/Oduo24/Savings-Loan-and-Investment-App/assets/82431848/0468e873-6d5b-42c4-99d1-569d70c752f0)

- Request for a loan.
  ![request-loan](https://github.com/Oduo24/Savings-Loan-and-Investment-App/assets/82431848/84184d57-7f8e-4d6e-88fe-bd3a891c363a)

- Approve loan requests.
  ![approve-loan](https://github.com/Oduo24/Savings-Loan-and-Investment-App/assets/82431848/f2f7c726-2d65-4a9e-8b05-0fd2aa90eede)

- View their transaction history.
- View loan history.
