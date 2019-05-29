# -*- coding: utf-8 -*-
# Author: XuMing <xuming624@qq.com>
# Brief: config
import os

this_dir = os.path.dirname(os.path.abspath(__file__))

# 通用分词词典文件  format: 词语 词频
word_freq_path = this_dir + "/" + 'data/word_freq.txt'
# 中文常用字符集
common_char_path = this_dir + "/" + 'data/common_char_set.txt'
# 同音字
same_pinyin_path = this_dir + "/" + 'data/same_pinyin.txt'
# 形似字
same_stroke_path = this_dir + "/" + 'data/same_stroke.txt.bak'
# language model path
language_model_path = this_dir + "/" + '../data/language_model_data/renmin/people_chars_lm.klm'
#language_model_path = this_dir + "/" + '../data/language_model_data/renmin/people2014corpus_chars.klm'
#language_model_path = this_dir + "/" + '../data/language_model_data/wiki/lm_char.klm'
# language_model_path = this_dir + "/" +'../data/kenlm/char_kenlm.model'
# 用户自定义错别字混淆集  format:变体	本体   本体词词频（可省略）
custom_confusion_path = this_dir + "/" + 'data/custom_confusion.txt'
# 用户自定义分词词典  format: 词语 词频
custom_word_freq_path = this_dir + "/" + 'data/custom_word_freq.txt'
# 知名人名词典 format: 词语 词频
person_name_path = this_dir + "/" + 'data/person_name.txt'
# 地名词典 format: 词语 词频
place_name_path = this_dir + "/" + 'data/place_name.txt'
# 停用词
stopwords_path = this_dir + "/" + 'data/stopwords.txt'
