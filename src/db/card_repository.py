from db.model import Card

SPLIT_CARD_JOIN = '/'
SUFFIXES_TO_STRIP = (' (a)', ' (b)')

def get_card_from_first_expansion(session, expansion_ids, name):
    for expansion_id in expansion_ids:
        result = session.query(Card).filter_by(expansion=expansion_id, name=name).one_or_none()
        if result:
            return result

    return None

def get_card_by_id(session, id):
    return session.query(Card).filter_by(id=id).one_or_none()

def get_card(session, expansion_id, number=None, name=None, face=None):
    query = session.query(Card).filter_by(expansion=expansion_id)
    if number is not None:
        query = query.filter_by(number=number)
    if name is not None:
        query = query.filter_by(name=name)
    if face is not None:
        query = query.filter_by(face=face)

    all_matches = query.order_by(Card.number).all()
    if len(all_matches) == 0:
        return None
    result = all_matches[0]
    if not result.type.startswith('Basic Land - '):
        assert len(all_matches) == 1, f'Found multiple matches for name "{name}" number {number} face {face} in {expansion_id}'
    return result


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
