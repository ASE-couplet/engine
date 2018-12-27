import argparse
import time
import random
import sys

from sqlalchemy import create_engine, MetaData, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

import ipdb

test_tags = ["雪，月", "风，花", "树，鸟", "雷，云"]

def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--Mode', type=str, 
        help='server or dev',
        default='server')
    return parser.parse_args(argv)

if __name__ == "__main__":
    mode = parse_arguments(sys.argv[1:]).Mode

    if mode == "dev":
        engine = create_engine('sqlite:///test_couplet.db?check_same_thread=False', echo=False)
    else:
        engine = create_engine("postgresql+psycopg2://poemscape@poemscape")
    # # # Creating the table : ---------------
    # from sqlalchemy import Column,Integer,String

    # Base = declarative_base()

    # class Order(Base):
    #     __tablename__ = 'Order'

    #     id = Column(Integer, primary_key=True)
    #     image = Column(String)
    #     tags = Column(String)
    #     poems = Column(String)

    # Base.metadata.create_all(engine)

    # ipdb.set_trace() 

    metadata = MetaData()
    metadata.reflect(engine, only=['api_order'])
    Base = automap_base(metadata=metadata)
    Base.prepare()
    Order = Base.classes.api_order
    Session = sessionmaker(bind=engine)
    sess = Session()
    for i in range(100):
        randn = random.randint(100000,200000)
        sess.add(Order(id=randn, image=str(randn) +".png", tags=test_tags[randn % 4]))  
        sess.commit()
        time.sleep(5)
        item = sess.query(Order).filter_by(id=randn).first()
        print(item.poem)
