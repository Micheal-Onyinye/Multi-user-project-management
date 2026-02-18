from fastapi import FastAPI
from app.routes import auth, organization

app = FastAPI(title="Multi-Tenant Project Management API")

app.include_router(auth.router)

app.include_router(organization.router)

app.include_router(invitation.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)