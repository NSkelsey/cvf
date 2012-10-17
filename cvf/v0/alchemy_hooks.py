from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os


engine = create_engine('mysql://dba:mypass@localhost:3306/forum', echo=True)
DBSession = scoped_session(sessionmaker(bind=engine))
session = DBSession()

cmd = "sqlautocode mysql://dba:mypass@localhost:3306/forum -o alchemy_models.py --force"

if __name__ == "__main__":
    os.system(cmd)
    f = open('alchemy_models.py', 'r')
    s = f.read()
    f.close()
    regex = "databases"
    f = open('alchemy_models.py', 'w')
    s = s.replace(regex, 'dialects', 1)
    f.write(s)
