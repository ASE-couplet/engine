#!/usr/bin/env python
# coding: utf-8


import json

import tensorflow as tf

import random

from kernel.data_utils import prepare_batch_predict_data
from kernel.model import Seq2SeqModel
from kernel.vocab import get_vocab, ints_to_sentence

# Data loading parameters
tf.app.flags.DEFINE_boolean('rev_data', True, 'Use reversed training data')
tf.app.flags.DEFINE_boolean('align_data', True, 'Use aligned training data')
tf.app.flags.DEFINE_boolean('prev_data', True, 'Use training data with previous sentences')
tf.app.flags.DEFINE_boolean('align_word2vec', True, 'Use aligned word2vec model')

# Decoding parameters
tf.app.flags.DEFINE_integer('beam_width', 1, 'Beam width used in beamsearch')
tf.app.flags.DEFINE_integer('decode_batch_size', 80, 'Batch size used for decoding')
tf.app.flags.DEFINE_integer('max_decode_step', 500, 'Maximum time step limit to decode')
tf.app.flags.DEFINE_boolean('write_n_best', False, 'Write n-best list (n=beam_width)')
tf.app.flags.DEFINE_string('model_path', 'predict_poetry/kernel/model/translate.ckpt-809500', 'Path to a specific model checkpoint.')
tf.app.flags.DEFINE_string('model_dir', None, 'Path to load model checkpoints')
tf.app.flags.DEFINE_string('predict_mode', 'sample', 'Decode helper to use for predicting')
tf.app.flags.DEFINE_string('decode_input', 'data/newstest2012.bpe.de', 'Decoding input path')
tf.app.flags.DEFINE_string('decode_output', 'data/newstest2012.bpe.de.trans', 'Decoding output path')

# Runtime parameters
tf.app.flags.DEFINE_boolean('allow_soft_placement', True, 'Allow device soft placement')
tf.app.flags.DEFINE_boolean('log_device_placement', False, 'Log placement of ops on devices')


FLAGS = tf.app.flags.FLAGS


#json loads strings as unicode; we currently still work with Python 2 strings, and need conversion
def unicode_to_utf8(d):
    return dict((key.encode("UTF-8"), value) for (key, value) in list(d.items()))


def load_config(FLAGS):
    if FLAGS.model_path is not None:
        checkpoint_path = FLAGS.model_path
        print('Model path specified at: {}'.format(checkpoint_path))
    elif FLAGS.model_dir is not None:
        checkpoint_path = tf.train.latest_checkpoint(FLAGS.model_dir + '/')
        print('Model dir specified, using the latest checkpoint at: {}'.format(checkpoint_path))
    else:
        checkpoint_path = tf.train.latest_checkpoint('model/')
        print('Model path not specified, using the latest checkpoint at: {}'.format(checkpoint_path))

    FLAGS.model_path = checkpoint_path

    # Load config saved with model
    config_unicode = json.load(open('%s.json' % FLAGS.model_path, 'rb'))
    # config = unicode_to_utf8(config_unicode)
    config = config_unicode

    # Overwrite flags
    for key, value in list(FLAGS.__flags.items()):
        config[key] = value

    return config


def load_model(session, model, saver):
    if tf.train.checkpoint_exists(FLAGS.model_path):
        print('Reloading model parameters..')
        model.restore(session, saver, FLAGS.model_path)
    else:
        raise ValueError(
            'No such file:[{}]'.format(FLAGS.model_path))
    return model


class Seq2SeqPredictor:
    def __init__(self):
        # Load model config
        config = load_config(FLAGS)

        config_proto = tf.ConfigProto(
            allow_soft_placement=FLAGS.allow_soft_placement,
            log_device_placement=FLAGS.log_device_placement,
            gpu_options=tf.GPUOptions(allow_growth=True)
        )

        self.sess = tf.Session(config=config_proto)

        # Build the model
        self.model = Seq2SeqModel(config, 'predict')

        # Create saver
        # Using var_list = None returns the list of all saveable variables
        saver = tf.train.Saver(var_list=None)

        # Reload existing checkpoint
        load_model(self.sess, self.model, saver)

        # load faces
        self.girl_poetry = None
        self.boy_poetry = None
        self.people_poetry = None
        self.load_face()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sess.close()

    def load_face(self):
        girls = []
        boys = []
        people = []
        with open('./predict_poetry/boys_poetry.txt', 'r', encoding='utf-8') as f_in:
            for line in f_in.readlines():
                data = line.strip().split()
                if len(data) != 4:
                    print(boys)
                    print('boys poetry loaded')
                    break
                boys.append(data)
        with open('./predict_poetry/girls_poetry.txt', 'r', encoding='utf-8') as f_in:
            for line in f_in.readlines():
                data = line.strip().split()
                if len(data) != 4:
                    print(girls)
                    print('girls poetry loaded')
                    break
                girls.append(data)
        with open('./predict_poetry/people_poetry.txt', 'r', encoding='utf-8') as f_in:
            for line in f_in.readlines():
                data = line.strip().split()
                if len(data) != 4:
                    print(people)
                    print('people poetry loaded')
                    break
                people.append(data)
        self.girl_poetry = girls
        self.boy_poetry = boys
        self.people_poetry = people


    def predict(self, keywords):
        sentences = []
        i_keyword = 0
        for keyword in keywords:
            if '男' in keyword:
                return random.sample(self.boy_poetry, 1)[0]
            elif '女' in keyword:
                return random.sample(self.girl_poetry, 1)[0]
        for keyword in keywords:
            if '人' in keyword:
                return random.sample(self.people_poetry, 1)[0]
        while len(sentences) != 4:
            keyword = keywords[i_keyword]
            source, source_len = prepare_batch_predict_data(keyword,
                                                            previous=sentences,
                                                            prev=FLAGS.prev_data,
                                                            rev=FLAGS.rev_data,
                                                            align=FLAGS.align_data)

            predicted_batch = self.model.predict(
                self.sess,
                encoder_inputs=source,
                encoder_inputs_length=source_len
            )

            predicted_line = predicted_batch[0] # predicted is a batch of one line
            predicted_line_clean = predicted_line[:-1] # remove the end token
            predicted_ints = [x[0] for x in predicted_line_clean] # Flatten from [time_step, 1] to [time_step]
            predicted_sentence = ints_to_sentence(predicted_ints)

            if FLAGS.rev_data:
                predicted_sentence = predicted_sentence[::-1]
            if legal(predicted_sentence):
                sentences.append(predicted_sentence)
                i_keyword = i_keyword + 1
        return sentences


def legal(sentence):
    neg_dict = ['浊', '病', '死', '杀', '骨', '贱', '哀', '催', '盲', '猩', '哭', '']
    for i in range(len(sentence)):
        if sentence[i] in neg_dict:
            return False
        for j in range(i+1, len(sentence)):
            if sentence[i] == sentence[j]:
                if not (i + 1 == j and sentence[i] in ["盈盈", '脉脉']):
                    return False
    return True

def main(_):
    KEYWORDS = [
        '楚',
        '收拾',
        '思乡',
        '相随'
    ]

    with Seq2SeqPredictor() as predictor:
        lines = predictor.predict(KEYWORDS)
        for line in lines:
            print(line)

if __name__ == '__main__':
    tf.app.run()
