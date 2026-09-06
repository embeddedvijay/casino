

from database import db
from admin.services.auth_service import new_password_record

new_password = "Gold365@2026"
password_hash, password_salt = new_password_record(new_password)

db.clients.update_one(
    {"client_id": "demo"},
    {
        "$set": {
            "password_hash": password_hash,
            "password_salt": password_salt,
            "must_change_password": False
        }
    }
)

db.admin_sessions.delete_many({"username": "demo"})

print("Password reset successfully")
print("Username: demo")
print("Password: Demo@123")

'''
ab hme ek admin application banana hai do db se connect hoga configure krega users details show krega full balance update user activate deativa.

'''