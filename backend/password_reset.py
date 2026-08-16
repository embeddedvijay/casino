

from database import db
from admin.services.auth_service import new_password_record

new_password = "Demo@123"
password_hash, password_salt = new_password_record(new_password)

db.clients.update_one(
    {"client_id": "demo"},
    {
        "$set": {
            "password_hash": password_hash,
            "password_salt": password_salt,
            "must_change_password": True
        }
    }
)

db.admin_sessions.delete_many({"username": "demo"})

print("Password reset successfully")
print("Username: demo")
print("Password: Demo@123")
