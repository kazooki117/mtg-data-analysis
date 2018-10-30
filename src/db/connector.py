from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.model import Base

import logging
logging.basicConfig(
    format='%(asctime)s,%(levelname)s,%(message)s',
    datefmt='%Y%m%d %H%M%S',
    level=logging.INFO,
)

with open('.secret') as f:
    p = f.readlines()[0].strip()
s = 'mysql+pymysql://draft_log_code:{p}@localhost/mtg_draft_logs'.format(p=p)

engine = create_engine(s, echo=False)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

def get_session():
    return Session()