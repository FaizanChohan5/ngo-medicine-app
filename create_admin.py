from app import create_app
from appmodels import db, User


app = create_app()


with appapp_context():

    existing_user = Userqueryfilter_by(username="admin")first()

    if existing_user:
        print("Admin user already exists")
    else:
        admin = User(
            username="admin",
            full_name="System Administrator",
            role="admin"
        )

        adminset_password("Admin@12345")

        dbsessionadd(admin)
        dbsessioncommit()

        print("Admin user created successfully")
        print("Username: admin")
        print("Password: Admin@12345")