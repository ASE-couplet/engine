import argparse
import os
import sys
import logging
import time

from sqlalchemy import create_engine, MetaData, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

from predict_poetry.api import img2tag

logging.basicConfig(level=logging.WARNING)

def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--Mode', type=str, 
        help='server or dev',
        default='server')
    return parser.parse_args(argv)

if __name__ == "__main__":
    mode = parse_arguments(sys.argv[1:]).Mode
    if mode == "dev":
        engine = create_engine('sqlite:///test_couplet.db?check_same_thread=False')
    else:
        engine = create_engine("postgresql+psycopg2://poemscape@poemscape")
    metadata = MetaData()
    metadata.reflect(engine, only=['api_order'])
    Base = automap_base(metadata=metadata)
    Base.prepare()
    Order = Base.classes.api_order
    Session = sessionmaker(bind=engine)
    while(1):
        sess = Session()
        target_orders = sess.query(Order).filter_by(tags=None)
        for item in target_orders:
            if mode != "dev":
                item.tags = img2tag('http://poemscape.mirrors.asia/media/' + item.image)  
            sess.commit()
            logging.debug("Making tags for id:{} tags:{}".format(item.id, item.tags))
        time.sleep(1)