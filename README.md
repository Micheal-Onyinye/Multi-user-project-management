# Multi-Tenant Project Management API
A backend API built with FastAPI that allows multiple organizations to manage projects and tasks in a secure multi-tenant environment. The system supports organization management, user invitations, project creation, and task creation with role-based access control.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [API Example Flows](#api-example-flows)
- [Project Outcome](#project-outcome)


## Overview

This project demonstrates a multi-tenant backend architecture where multiple organizations can use the same system while keeping their data completely isolated.

Each organization can:

- Invite members
- Create projects
- create tasks
- Manage team collaboration

## Architecture

The project follows a layered architecture:
```
MULTI-TENANT 
│
├── app
│   │
│   ├── core                
│   │   ├── config.py
│   │   ├── security.py
│   │   └── permissions.py
│   │
│   ├── db                 
│   │   ├── database.py
│   │   └── seed.py
│   │
│   ├── models            
│   │   ├── user.py
│   │   ├── organization.py
│   │   ├── project.py
│   │   ├── task.py
│   │   └── invitation.py
│   │
│   ├── schemas             
│   │   ├── user.py
│   │   ├── organization.py
│   │   ├── project.py
│   │   ├── task.py
│   │   └── invitation.py
│   │
│   └── routes              
│       ├── auth.py
│       ├── organizations.py
│       ├── projects.py
│       ├── tasks.py
│       └── invitations.py
│
├── main.py                 
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## Features

### Authentication
- User registration
- Login with JWT tokens

### Organization Management
- Create organizations
- Role-based membership

### Invitations
- Invite users to organizations
- Accept or reject invitations

### Projects
- Create projects inside organizations
- Restrict access to members

### Tasks
- Create tasks
- Update task details
- Change task status


## Tech Stack

Backend Framework  
- FastAPI

Database  
- PostgreSQL

ORM  
- SQLAlchemy

Validation  
- Pydantic

Authentication  
- JWT

Server  
- Uvicorn


## Installation

### 1. Clone the repository

git clone https://github.com/Micheal-Onyinye/Multi-user-project-management.git

cd multi-tenant

### 2. Install dependencies

pip install -r requirements.txt

### 3. Configure environment variables

Create a `.env` file

DATABASE_URL=postgresql://postgres:password@localhost/multi_tenant
SECRET_KEY=your_secret_key


### 4. Run the server

uvicorn app.main:app --reload

## API Example Flows

### Create Organization

POST /organizations

Example request:

{
  "name": "Tech Company"
}

Result:
Organization created and the creator becomes the admin.


POST /organizations/{org_id}/invitations

{
  "email": "member@example.com",
  "role": "Member"
}


POST /organizations/{org_id}/projects

{
  "name": "Internal CRM"
}

POST /organizations/{org_id}/projects/{project_id}/tasks

{
  "title": "Design database schema",
  "description": "Prepare tables and relationships",
  "assignee_id": 2
}


## Project Outcome

This project demonstrates:

- Multi-tenant backend architecture
- Secure API design
- Role-based access control
- PostgreSQL relational modeling
- Clean FastAPI structure

The system can serve as a foundation for SaaS collaboration platforms.
