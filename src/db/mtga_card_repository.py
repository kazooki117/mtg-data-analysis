from db.model import MTGACard

def get_mtga_card(session, mtga_id):
    return session.query(MTGACard).filter_by(mtga_id=mtga_id).one_or_none()
