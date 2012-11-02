import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, mapper, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sabridge import Bridge

from cvf.v0 import models

Base = declarative_base()
engine = create_engine('mysql://dba:mypass@localhost:3306/forum', echo=True)
DBSession = scoped_session(sessionmaker(bind=engine))
session = DBSession()

bridge = Bridge()
sa_post = bridge[models.Post]
sa_relvote = bridge[models.RelVote]

cmd = "sqlautocode mysql://dba:mypass@localhost:3306/forum -o alchemy_models.py --force"

class SA_Post(Base):
    __table__ = sa_post

SA_Post.children = relationship("Node",
                backref=backref('parent', remote_side=[id])
            )



if __name__ == "__main__":
    os.system(cmd)
    f = open('alchemy_models.py', 'r')
    s = f.read()
    f.close()
    regex = "databases"
    f = open('alchemy_models.py', 'w')
    s = s.replace(regex, 'dialects', 1)
    f.write(s)
