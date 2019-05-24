# -*- coding: utf-8 -*-
"""
@author:XuMing（xuming624@qq.com)
@description: 
"""
import re

from pycorrector import Corrector

from pycorrector.config import common_char_path, same_pinyin_path, \
    same_stroke_path, language_model_path, \
    word_freq_path, \
    custom_confusion_path, place_name_path, person_name_path, stopwords_path,custom_word_freq_path

# 使用三元文法语言模型（people_chars.klm）纠错效果更好：
# language_model_path = '../pycorrector/data/kenlm/people_chars.klm'
model = Corrector(common_char_path=common_char_path,
                  same_pinyin_path=same_pinyin_path,
                  same_stroke_path=same_stroke_path,
                  language_model_path=language_model_path,
                  word_freq_path=word_freq_path,
                  custom_word_freq_path=custom_word_freq_path,
                  custom_confusion_path=custom_confusion_path,
                  person_name_path=person_name_path,
                  place_name_path=place_name_path,
                  stopwords_path=stopwords_path
                  )

error_sentences = [
    # "报单什么时候",
    # "现金利益给付几天到帐",
    # "理赔金额咋没到帐",
    "定购一个苹果手机",
    "暴发战争",
    "布署服务",
    "备受折磨",
    "饿，不是我",
    "报销怎么操做",
    "保单中止如何办理",
    "办理减额交清所需资料"
]

for line in error_sentences:
    correct_sent = model.correct(line)
    # print(correct_sent)
    # re.sub(" ", "", correct_sent)
    print("original sentence:{} => correct sentence:{}".format(line, correct_sent))

