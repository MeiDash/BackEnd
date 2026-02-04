from app.db import SessionLocal
from app.models import User

db = SessionLocal()
users = db.query(User).all()
for user in users:
    print(f'User: id={user.id}, email={user.email}, is_active={user.is_active}, hashed_password={user.hashed_password}')
db.close()