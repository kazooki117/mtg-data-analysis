from db.model import User

def get_user(session, username):
    return session.query(User).filter_by(username=username).one_or_none()
