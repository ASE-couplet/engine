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

logging.basicConfig(level=logging.DEBUG)

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
        logging.debug( lines[0]+'('+keywords[0]+')  '+lines[1]+'('+keywords[1]+')' )
        return lines[0]+'   '+lines[1]

if __name__ == "__main__":
    maker = Main_Poetry_maker()
    engine = create_engine('sqlite:///test_couplet.db?check_same_thread=False', echo=False)
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
            logging.info("Making poems for id:{} poems:{}".format(item.id, item.poems))
