from db.model import Card

SPLIT_CARD_JOIN = '/'
SUFFIXES_TO_STRIP = (' (a)', ' (b)')

def get_card_from_first_expansion(session, expansion_ids, name):
    for expansion_id in expansion_ids:
        result = session.query(Card).filter_by(expansion=expansion_id, name=name).one_or_none()
        if result:
            return result

    return None

def get_card(session, expansion_id, number=None, name=None, face=None):
    query = session.query(Card).filter_by(expansion=expansion_id)
    if number is not None:
        query = query.filter_by(number=number)
    if name is not None:
        query = query.filter_by(name=name)
    if face is not None:
        query = query.filter_by(face=face)
    return query.one_or_none()


def get_card_by_approximate_name(session, expansion_id, name):
    if SPLIT_CARD_JOIN in name:
        name = name[:name.find(SPLIT_CARD_JOIN)]

    name = name.strip()

    result = get_card(session, expansion_id=expansion_id, name=name)
    if result is not None:
        return result

    for suffix in SUFFIXES_TO_STRIP:
        result = get_card(session, expansion_id=expansion_id, name=f'{name}{suffix}')
        if result is not None:
            return result
