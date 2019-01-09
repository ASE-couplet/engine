import argparse
import os
import sys
import logging
import time

from PIL import Image
from sqlalchemy import create_engine, MetaData, Column, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

from predict_poetry.api import img2tag

logging.basicConfig(level=logging.WARNING)

image_dir = "/var/opt/poemscape/media"

def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--Mode', type=str, 
        help='server or dev',
        default='server')
    return parser.parse_args(argv)

def process_image(filename):
    fsize = os.path.getsize(filename)
    image = Image.open(filename)
    w,h = image.size
    scale = 2
    new_im = image.resize((int(w/scale), int(h/scale)), Image.ANTIALIAS) 
    new_im.save(filename)
    new_im.close()

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
        target_orders = sess.query(Order).filter(Order.tags==None)
        for item in target_orders:
            if mode != "dev":
                fsize = os.path.getsize(os.path.join(image_dir, item.image))
                try:
                    if fsize > 4000000:
                        raise RuntimeError("Too large Image")
                    if fsize > 4194304 :
                        process_image(os.path.join(image_dir, item.image))
                    item.tags = img2tag("http://poemscape.mirrors.asia/media/" + item.image)
                except Exception as e:
                    logging.error(e)
                    item.tags = "笑"
            sess.commit()
            logging.warning("Making tags for id:{} poems:{}".format(item.id, item.tags))
        sess.close()
        time.sleep(0.5)
