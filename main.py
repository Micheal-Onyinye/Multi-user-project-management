from fastapi import FastAPI
from app.routes import auth, organization, invitations, tasks, projects, activities
from app.db.database import Base, engine

app = FastAPI(title="Multi-Tenant Project Management API")

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)

app.include_router(organization.router)

app.include_router(invitations.router)

app.include_router(tasks.router)

app.include_router(projects.router)

app.include_router(activities.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)