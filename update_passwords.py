from app.db import SessionLocal
from app.models import User
from app.core.security import hash_password

db = SessionLocal()
users = db.query(User).all()
for user in users:
    if user.email == 'admin@example.com':
        user.hashed_password = hash_password('admin123')
    elif user.email == 'test@example.com':
        user.hashed_password = hash_password('test123')
    print(f'Updated {user.email}')
db.commit()
db.close()