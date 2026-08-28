from app import create_app
from appmodels import db, User


app = create_app()


with appapp_context():

    # Create Store User
    store_user = Userqueryfilter_by(username="store")first()

    if not store_user:

        store_user = User(
            username="store",
            full_name="Store Person",
            role="store"
        )

        store_userset_password("Store@12345")

        dbsessionadd(store_user)

        print("Store user created")

    else:
        print("Store user already exists")

    # Create Field User
    field_user = Userqueryfilter_by(username="field1")first()

    if not field_user:

        field_user = User(
            username="field1",
            full_name="Field Person 1",
            role="field"
        )

        field_userset_password("Field@12345")

        dbsessionadd(field_user)

        print("Field user created")

    else:
        print("Field user already exists")

    dbsessioncommit()

    print("User setup completed")