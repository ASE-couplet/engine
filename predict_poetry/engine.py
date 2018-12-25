import argparse
import sys
import logging

import tensorflow as tf
from sqlalchemy import create_engine, MetaData, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

from plan import Planner
from predict import Seq2SeqPredictor
from match import MatchUtil

import ipdb

logging.basicConfig(level=logging.WARNING)

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
        logging.debug( lines[0]+'('+keywords[0]+')  '+lines[1]+'('+keywords[1]+')'+lines[2]+'('+keywords[2]+')'+lines[3]+'('+keywords[3]+')' )
        return lines[0]+'   '+lines[1]+'   '+lines[2]+'   '+lines[3]

if __name__ == "__main__":
    mode = parse_arguments(sys.argv[1:]).Mode
    if mode == "dev":
        engine = create_engine('sqlite:///test_couplet.db?check_same_thread=False', echo=False)
    else:
        engine = create_engine("postgresql+psycopg2://poemscape:@poemscape.db", echo=True)
    maker = Main_Poetry_maker()
    metadata = MetaData()
    metadata.reflect(engine, only=['Order'])
    Base = automap_base(metadata=metadata)
    Base.prepare()
    Order = Base.classes.Order
    Session = sessionmaker(bind=engine)
    sess = Session()
    while(1):
        target_orders = sess.query(Order).filter_by(poems=None)
        for item in target_orders:
            item.poems = maker.predict(item.tags)
            sess.commit()
            logging.warning("Making poems for id:{} poems:{}".format(item.id, item.poems))