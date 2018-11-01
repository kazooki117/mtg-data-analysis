from db.model import Draft

def get_draft(session, name):
    return session.query(Draft).filter_by(name=name).one_or_none()
