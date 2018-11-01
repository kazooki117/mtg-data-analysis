from db.model import Expansion

def get_expansion(session, name=None, abbreviation=None):
    query = session.query(Expansion)
    if name is not None:
        query = query.filter_by(name=name)
    if abbreviation is not None:
        query = query.filter_by(abbreviation=abbreviation)
    return query.one_or_none()
