# MyCoursePicker (MCP)

A modern web application that helps students make informed decisions about their course selections by providing AI-powered insights and historical data.

## Features

- Course information scraping from university catalog
- Student reviews and ratings from Reddit
- AI-powered insights using multiple LLM providers
- Modern, responsive UI built with React
- FastAPI backend with Python

## Project Structure

```
myCoursePicker/
├── frontend/           # React frontend application
├── backend/           # FastAPI backend application
│   ├── app/          # Main application code
│   ├── config/       # Configuration files
│   └── tests/        # Backend tests
└── README.md         # This file
```

## Setup Instructions

### Backend Setup

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your API keys and configurations
```

4. Run the backend:

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. Install dependencies:

```bash
cd frontend
npm install
```

2. Run the development server:

```bash
cd frontend
npm start
```

## Running the Service

To run the complete MyCoursePicker application:

### Quick Start (Recommended)

1. **Start the Backend Server:**

   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The backend API will be available at `http://localhost:8000`

2. **Start the Frontend Server:**
   ```bash
   cd frontend
   npm start
   ```
   The React app will automatically open at `http://localhost:3000`

### Background Mode

To run both services in the background:

1. **Backend (in background):**

   ```bash
   cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
   ```

2. **Frontend (in background):**
   ```bash
   cd frontend && npm start &
   ```

### Accessing the Application

- **Frontend UI:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

### Stopping the Services

- Use `Ctrl+C` in the terminal to stop the services
- If running in background, use `pkill -f uvicorn` and `pkill -f "npm start"` to stop them

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for the interactive API documentation.
