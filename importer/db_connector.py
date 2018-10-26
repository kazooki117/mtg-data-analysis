from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model import Base, Expansion, Card, User, Draft, DraftSeat, Pack, PackCard, Pick

with open('.secret') as f:
  p = f.readlines()[0].strip()
s = 'mysql+pymysql://draft_log_code:{p}@localhost/mtg_draft_logs'.format(p=p)

engine = create_engine(s, echo=False)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

def getSession():
  return Session()