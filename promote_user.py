from app import app, db, User
from sqlalchemy import select

with app.app_context():  # <-- Fixed: use 'app.app_context()' instead
    admin_user = db.session.scalars(select(User).filter_by(username='David')).first()
    if admin_user:
        admin_user.role = 'admin'
        db.session.commit()
        print("User successfully promoted to Admin!")
    else:
        print("User not found. Make sure the username matches exactly.")
