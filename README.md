# Resume Parser Web Application

## Fundamentals of Software Engineering Project — Spring 2025  
**FAST NUCES, Karachi**

---

## Group Members

- **Syed Areeb Hussain** — 22K-4042  
- **Syed Huzaifa Ali** — 23K-0004  
- **Haris Ahmed** — 23K-6005  

---

## Tech Stack

- **Backend:** Django REST Framework  
- **Frontend:** Django Templates + Tailwind CSS (with minimal custom CSS)  
- **NLP Library:** spaCy  
- **AI Integration:** OpenAI API *(temporarily disabled due to billing issues)*  
- **Database:** SQLite  

---

## Overview

The Resume Parser is a full-stack Django-based web application designed to automate and streamline the process of job posting, resume parsing, and skill-based filtering for recruiters, while offering resume submission and review features for job-seeking candidates.

---

## Django Apps Overview

### 1. `Users`  
Handles user **authentication and role management**.
- Signup and login using **TokenAuthentication**
- Role selection during signup (Candidate / Recruiter)
- Redirects users to their respective dashboards based on role

### 2. `Candidate`  
Manages all **candidate functionalities**.
- View all available jobs posted by recruiters  
- Apply to jobs with a simple resume upload form  
- Manage and update personal profile  
- AI resume review using OpenAI (currently inactive)

### 3. `Recruiter`  
Covers **recruiter-side features**.
- Post, edit, and delete job listings  
- View all applications received  
- Resume filtering based on skill keywords (e.g., "Python")  
- See detailed parsed skills only for resumes matching the searched keyword  
- Recruiter profile management

### 4. `AI_Analysis`  
Implements **resume parsing and analysis**.
- Parses uploaded resumes using **spaCy** to extract:
  - Skills
- Allows recruiters to filter candidates by skills  
- Uses **OpenAI API** to generate resume quality feedback *(currently disabled)*

---

## 🔑 Key Features

- ✅ Role-based authentication and navigation
- ✅ Resume upload with **file validation** (`.pdf` and `.docx` only)
- ✅ NLP-based resume parsing with **spaCy**
- ✅ Recruiter filtering of resumes based on required skills
- ✅ Recruiter-only access to detailed skill data
- ✅ Profile pages for both recruiters and candidates
- ✅ Minimalist, responsive frontend using **Tailwind CSS**
- ✅ REST API backend using Django REST Framework

---
