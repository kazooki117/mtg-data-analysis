from db.model import Expansion

def get_expansion(session, name):
    return session.query(Expansion).filter_by(name=name).one_or_none()
