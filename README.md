# 🔬 Science Exam Answer Prediction

An AI-powered web application for **Science Exam Answer Prediction**. The project provides a backend API for processing exam questions and predicting answers, along with a web-based frontend for interacting with the system.

## 🚀 Project Overview

The **Science Exam Answer Prediction** project is designed to demonstrate how Machine Learning/NLP-based prediction can be integrated into a complete web application.

The application consists of:

* 🧠 **Prediction Backend** — Python + FastAPI
* 🌐 **Frontend** — React + Vite
* 📊 **Evaluation/Metrics** — Python-based evaluation utilities
* 🧪 **Testing** — API test module
* 📁 **Sample Data** — CSV files for testing and demonstration

## 🏗️ Project Structure

```text
answer-predictor/
│
├── backend/
│   ├── main.py
│   ├── predictor.py
│   ├── metrics.py
│   ├── test_api.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.js
│
├── sample_test.csv
├── sample_test_with_answers.csv
└── .gitignore
```

## ⚙️ Technologies Used

### Backend

* Python
* FastAPI
* Uvicorn
* Pandas
* Scikit-learn

### Frontend

* React
* JavaScript
* Vite
* HTML
* CSS

### Development Tools

* Visual Studio Code
* Git
* GitHub
* Jupyter Notebook

## ✨ Features

* Science question answer prediction
* REST API-based backend
* Interactive web frontend
* Sample CSV data for testing
* Prediction and evaluation utilities
* API testing support
* Separate frontend and backend architecture

## 🖥️ Running the Backend

Open PowerShell in the project root:

```powershell
cd backend
```

Activate your virtual environment if required:

```powershell
..\..\.venv\Scripts\Activate.ps1
```

Install the backend dependencies:

```powershell
pip install -r requirements.txt
```

Start the FastAPI server:

```powershell
python -m uvicorn main:app --reload --port 8002
```

The backend will be available at:

```text
http://127.0.0.1:8002
```

FastAPI documentation:

```text
http://127.0.0.1:8002/docs
```

## 🌐 Running the Frontend

Open another PowerShell terminal:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Start the development server:

```powershell
npm run dev
```

Vite will display the local frontend URL in the terminal, usually:

```text
http://localhost:5173
```

## 🔄 Application Workflow

```text
User
  │
  ▼
React Frontend
  │
  │ HTTP Request
  ▼
FastAPI Backend
  │
  ▼
Prediction Module
  │
  ▼
Predicted Answer
  │
  ▼
Frontend Display
```

## 📊 Sample Data

The repository contains two sample datasets:

* `sample_test.csv`
* `sample_test_with_answers.csv`

These files can be used to test and demonstrate the prediction/evaluation workflow.

## 🧪 API Testing

The backend contains:

```text
backend/test_api.py
```

This file can be used to test the API functionality.

FastAPI also provides an interactive API interface at:

```text
http://127.0.0.1:8002/docs
```

## 📌 Project Purpose

This project was developed as a practical **Data Science / AI project** demonstrating the integration of:

* Data processing
* Prediction
* Evaluation
* REST APIs
* React frontend development
* Backend–frontend communication

## 🔮 Future Improvements

Possible future enhancements include:

* Improve prediction accuracy
* Add additional science subjects and datasets
* Add user authentication
* Add prediction history
* Add detailed answer explanations
* Add model performance dashboards
* Deploy the frontend and backend online
* Improve model evaluation and error analysis

## 👨‍💻 Author

**N.S Vathsan**

## 📄 License

This project is intended for educational and project demonstration purposes.
