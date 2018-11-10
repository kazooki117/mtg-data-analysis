from db.model import Deck

def get_deck(session, name):
    return session.query(Deck).filter_by(name=name).one_or_none()
