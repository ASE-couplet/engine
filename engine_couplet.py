import argparse
import os
import sys
import logging
import time

import tensorflow as tf
from sqlalchemy import create_engine, MetaData, Column, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

sys.path.append("./predict_couplet")
from predict_couplet.plan import Planner
from predict_couplet.predict import Seq2SeqPredictor
from predict_couplet.match import MatchUtil

logging.basicConfig(level=logging.WARNING)

card_dir = "/var/opt/poemscape/media/card"
image_dir = "/var/opt/poemscape/media"

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
    if mode != "dev":
        engine =  engine = create_engine("postgresql+psycopg2://poemscape:asepoemscape@poemscape.mirrors.asia:5432/poemscape")
    else:
        engine = create_engine("postgresql+psycopg2://poemscape@poemscape")
    maker = Main_Poetry_maker()
    metadata = MetaData()
    metadata.reflect(engine, only=['api_order'])
    Base = automap_base(metadata=metadata)
    Base.prepare()
    Order = Base.classes.api_order
    Session = sessionmaker(bind=engine)
    sess = Session()
    while(1):
        target_orders = sess.query(Order).filter(and_(Order.couplet==None, Order.tags!=None))
        for item in target_orders:
            if mode != "dev":
                try:
                    item.couplet = maker.predict(item.tags)
                except:
                    item.couplet = "窗前明月光\n疑是地上霜\n"   
            sess.commit()
            logging.warning("Making poems for id:{} poems:{}".format(item.id, item.couplet))
        sess.close()
        time.sleep(1)
