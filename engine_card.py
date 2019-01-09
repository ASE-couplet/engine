import argparse
import os
import sys
import logging
import time

from sqlalchemy import create_engine, MetaData, Column, and_, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

from generate_card import generate_card

logging.basicConfig(level=logging.WARNING)

card_dir = "/var/opt/poemscape/media/card"
couplet_card_dir = "/var/opt/poemscape/media/couplet_card"
image_dir = "/var/opt/poemscape/media"

def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--Mode', type=str, 
        help='server or dev',
        default='server')
    return parser.parse_args(argv)

if __name__ == "__main__":
    mode = parse_arguments(sys.argv[1:]).Mode
    if mode != "dev":
        engine =  engine = create_engine("postgresql+psycopg2://poemscape:asepoemscape@poemscape.mirrors.asia:5432/poemscape")
    else:
        engine = create_engine("postgresql+psycopg2://poemscape@poemscape")
    metadata = MetaData()
    metadata.reflect(engine, only=['api_order'])
    Base = automap_base(metadata=metadata)
    Base.prepare()
    Order = Base.classes.api_order
    Session = sessionmaker(bind=engine)
    sess = Session()
    while(1):
        # import ipdb
        # ipdb.set_trace()
        target_orders = sess.query(Order).filter(and_(or_(Order.card==None, Order.card==''), Order.poem!=None))
        for item in target_orders:
            if mode != "dev":
                try:
                    generate_card.generate_card(os.path.join(image_dir, item.image), item.poem, \
                                        os.path.join(card_dir, str(item.id)+".png"))
                    item.card = "card/" + str(item.id) + ".png"
                except Exception as e:
                    logging.error(e)
                    item.card = "card/" + str(66) + ".png"
                sess.commit()
                logging.warning("Making card for id:{} poems:{}".format(item.id, item.card))

        target_orders = sess.query(Order).filter(and_(or_(Order.couplet_card==None, Order.couplet_card==''), Order.poem!=None))
        for item in target_orders:
            if mode != "dev":
                try:
                    generate_card.generate_card(os.path.join(image_dir, item.image), item.couplet, \
                                        os.path.join(couplet_card_dir, str(item.id)+".png"))
                    item.couplet_card = "couplet_card/" + str(item.id) + ".png"
                except Exception as e:
                    logging.error(e)
                    item.couplet_card = "card/" + str(66) + ".png"
                sess.commit()
                logging.warning("Making couplet_card for id:{} poems:{}".format(item.id, item.couplet_card))

        sess.close()
        time.sleep(0.5)
