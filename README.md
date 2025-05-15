# Resume Parser Project

This project consists of a Django backend API and a React frontend application for parsing and analyzing resumes.

## Project Structure

- `Resume_Parser/` - Django backend
- `FSE PROJECT/` - React frontend

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd Resume_Parser
   ```

2. Install the required dependencies:
   ```
   python -m pip install -r requirements.txt
   ```

3. Run migrations to set up the database:
   ```
   python manage.py migrate
   ```

4. Start the Django development server:
   ```
   python manage.py runserver
   ```
   The backend API will be available at http://localhost:8000/api

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd "FSE PROJECT"
   ```

2. Install the required dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```
   The frontend will be available at http://localhost:5173

## Quick Start

For convenience, you can use the provided batch script to start both servers at once:

```
start-servers.bat
```

## API Endpoints

### Authentication
- `POST /api/Users/login/` - User login
- `POST /api/Users/register/` - User registration
- `POST /api/Users/logout/` - User logout

### Candidate
- `GET /api/Candidate/profile/` - Get candidate profile
- `PUT /api/Candidate/profile/` - Update candidate profile
- `GET /api/Candidate/jobs/` - List available jobs
- `POST /api/Candidate/apply/` - Apply for a job

### Recruiter
- `GET /api/Recruiter/jobs/` - List recruiter's jobs
- `POST /api/Recruiter/jobs/` - Create a new job
- `PUT /api/Recruiter/jobs/<id>/` - Update a job
- `DELETE /api/Recruiter/jobs/<id>/` - Delete a job
- `POST /api/Recruiter/parse/all/` - Parse all resumes
- `POST /api/Recruiter/parse/selected/` - Parse selected resumes

### AI Analysis
- `POST /api/AI/analysis/` - Analyze a resume

## Implementation Details

- The frontend and backend are connected via API calls using the Fetch API
- CORS is enabled on the backend to allow requests from the frontend
- Authentication is handled using token-based authentication
- The frontend uses React context for state management