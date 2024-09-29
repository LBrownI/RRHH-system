from load_db import Session, User  # Import your session and User model

# Function for authenticating users
def authenticate(username, password):
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return None