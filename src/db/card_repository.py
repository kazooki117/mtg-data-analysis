from db.model import Card

def get_card(session, expansion_id, number, face=None):
    return session.query(Card).filter_by(expansion=expansion_id, number=number, face=face).one_or_none()
