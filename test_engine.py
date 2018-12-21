import time
import random

from sqlalchemy import create_engine, MetaData, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

import ipdb

test_tags = ["雪，月", "风，花", "树，鸟", "雷，云"]

if __name__ == "__main__":
    engine = create_engine('sqlite:///test_couplet.db?check_same_thread=False', echo=False)
    metadata = MetaData()
    metadata.reflect(engine, only=['Order'])
    Base = automap_base(metadata=metadata)
    Base.prepare()
    Order = Base.classes.Order
    Session = sessionmaker(bind=engine)
    sess = Session()
    # sess.add_all([
    #     Order(id=1, image="1.png", tags="雪，月"),
    #     Order(id=2, image="2.png", tags="风，花"),
    #     Order(id=3, image="3.png", tags="树，鸟"),
    #     Order(id=4, image="4.png", tags="雷，云"),
    # ])
    # sess.commit()
    # time.sleep(10)
    for i in range(1000):
        randn = random.randint(100000,200000)
        sess.add(Order(id=randn, image=str(randn) +".png", tags=test_tags[randn % 4]))  
        sess.commit()
        time.sleep(5)
        item = sess.query(Order).filter_by(id=randn).first()
        print(item.poems)
