from sqlalchemy.orm import Session
from app.models.role import Role

def seed_roles(db: Session):
    roles = ["Admin", "Member", "Viewer"]

    for role_name in roles:
        existing = db.query(Role).filter(Role.name == role_name).first()
        if not existing:
            db.add(Role(name=role_name))

    db.commit()
