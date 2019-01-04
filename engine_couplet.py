import argparse
import os
import sys
import logging
import time

import tensorflow as tf
from sqlalchemy import create_engine, MetaData, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

sys.path.append("./predict_couplet")
from predict_couplet.plan import Planner
from generate_card import generate_card
from predict_couplet.predict import Seq2SeqPredictor
from predict_couplet.match import MatchUtil

logging.basicConfig(level=logging.WARNING)

card_dir = "/var/opt/poemscape/media/couplet" # TODO
image_dir = "/var/opt/poemscape/media"

num_prepared = 10

def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--Mode', type=str, 
        help='server or dev',
        default='server')
    return parser.parse_args(argv)

class Main_Poetry_maker:
    def __init__(self):
        self.planner = Planner()
        self.predictor = Seq2SeqPredictor()
        self.Judge = MatchUtil()

    def predict(self, input_ustr):
        input_ustr = input_ustr.strip()
        keywords = self.planner.plan(input_ustr)
        lines = self.predictor.predict(keywords)
        result = self.Judge.eval_rhyme(lines)
        while(result == False):
            lines = self.predictor.predict(keywords)
            result = self.Judge.eval_rhyme(lines)
            no_dieci = self.Judge.dieci(lines)
            result = result and no_dieci
        logging.debug( lines[0]+'('+keywords[0]+')  '+lines[1]+'('+keywords[1]+')')
        return '\n'.join(lines) + '\n'


if __name__ == "__main__":
    mode = parse_arguments(sys.argv[1:]).Mode
    if mode == "dev":
        engine = create_engine('sqlite:///test_couplet.db?check_same_thread=False')
    else:
        engine = create_engine("postgresql+psycopg2://poemscape@poemscape")
    maker = Main_Poetry_maker()
    metadata = MetaData()
    metadata.reflect(engine, only=['api_order', 'api_couplet'])
    Base = automap_base(metadata=metadata)
    Base.prepare()
    Order = Base.classes.api_order
    Card = Base.classes.api_couplet
    Session = sessionmaker(bind=engine)
    while(1):
        sess = Session()
        all_orders = sess.query(Order).filter_by(poem=None)
        for item in all_orders:
            cards = sess.query(Card).filter_by(id==item.id)   # TODO
            requests = max(num_prepared - (len(cards) - item.couplet_viewed), 0)    # TODO
            for i in range(requests):
                tags = item.tags
                index = len(cards) + i + 1
                content = maker.predict(tags)
                generate_card.generate_card(os.path.join(image_dir, item.image), content, \
                            os.path.join(card_dir, str(item.id) + "_" + str(index) +".png"))
                card_pth = str(item.id) + "_" + str(index) +".png"
                product = Card(order=item.id, index=index, content=content, card=card_pth)
                sess.add(product) 
                logging.debug("Making poems for id:{} poems:{} index:{}".format(item.id, content, index))
                sess.commit()
        time.sleep(1)
