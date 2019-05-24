# -*- coding: utf-8 -*-
"""
@author:XuMing（xuming624@qq.com)
@description: use bert corrector chinese char error
"""
import sys
import os

sys.path.append('../..')
import torch
import operator
from pycorrector.config import language_model_path, word_freq_path, custom_word_freq_path, custom_confusion_path, \
    person_name_path, place_name_path, stopwords_path
from pycorrector.bert import config
from pycorrector.bert.bert_masked_lm import MASK_ID, InputFeatures
from pycorrector.corrector import error_type
from pycorrector.detector import Detector
from pycorrector.utils.text_utils import is_chinese_string
from pytorch_pretrained_bert import BertForMaskedLM
from pytorch_pretrained_bert.tokenization import BertTokenizer
import time

pwd_path = os.path.abspath(os.path.dirname(__file__))


class BertCorrector(Detector):
    def __init__(self, bert_model_dir='',
                 bert_model_vocab='',
                 max_seq_length=384):
        super(BertCorrector, self).__init__(language_model_path=language_model_path,
                                            word_freq_path=word_freq_path,
                                            custom_confusion_path=custom_confusion_path,
                                            custom_word_freq_path=custom_word_freq_path,
                                            person_name_path=person_name_path,
                                            place_name_path=place_name_path,
                                            stopwords_path=stopwords_path)
        self.name = 'bert_corrector'
        self.bert_model_dir = os.path.join(pwd_path, bert_model_dir)
        self.bert_model_vocab = os.path.join(pwd_path, bert_model_vocab)
        self.max_seq_length = max_seq_length
        self.initialized_bert_corrector = False

    def check_bert_corrector_initialized(self):
        if not self.initialized_bert_corrector:
            self.initialize_bert_corrector()

    def initialize_bert_corrector(self):
        t1 = time.time()
        self.bert_tokenizer = BertTokenizer(self.bert_model_vocab)
        # Prepare model
        self.model = BertForMaskedLM.from_pretrained(self.bert_model_dir)
        print("Loaded model: %s, vocab file: %s, spend: %.3f s." % (
            self.bert_model_dir, self.bert_model_vocab, time.time() - t1))
        self.initialized_bert_corrector = True

    def convert_sentence_to_features(self, sentence, tokenizer, max_seq_length, error_begin_idx=0, error_end_idx=0):
        """Loads a sentence into a list of `InputBatch`s."""
        self.check_bert_corrector_initialized()
        features = []
        tokens_a = list(sentence)

        # For single sequences:
        #  tokens:   [CLS] the dog is hairy . [SEP]
        #  type_ids: 0      0   0   0  0    0   0
        tokens = ["[CLS]"] + tokens_a + ["[SEP]"]
        k = error_begin_idx + 1
        for i in range(error_end_idx - error_begin_idx):
            tokens[k] = '[MASK]'
            k += 1
        segment_ids = [0] * len(tokens)

        input_ids = self.bert_tokenizer.convert_tokens_to_ids(tokens)
        mask_ids = [i for i, v in enumerate(input_ids) if v == MASK_ID]
        # The mask has 1 for real tokens and 0 for padding tokens. Only real
        # tokens are attended to.
        input_mask = [1] * len(input_ids)

        # Zero-pad up to the sequence length.
        padding = [0] * (max_seq_length - len(input_ids))
        input_ids += padding
        input_mask += padding
        segment_ids += padding

        features.append(
            InputFeatures(input_ids=input_ids,
                          input_mask=input_mask,
                          mask_ids=mask_ids,
                          segment_ids=segment_ids,
                          input_tokens=tokens))
        return features

    def check_vocab_has_all_token(self, sentence):
        self.check_bert_corrector_initialized()
        flag = True
        for i in list(sentence):
            if i not in self.bert_tokenizer.vocab:
                flag = False
                break
        return flag

    def bert_lm_infer(self, sentence, error_begin_idx=0, error_end_idx=0):
        self.check_bert_corrector_initialized()
        corrected_item = sentence[error_begin_idx:error_end_idx]
        eval_features = self.convert_sentence_to_features(
            sentence=sentence,
            tokenizer=self.bert_tokenizer,
            max_seq_length=self.max_seq_length,
            error_begin_idx=error_begin_idx,
            error_end_idx=error_end_idx
        )

        for f in eval_features:
            input_ids = torch.tensor([f.input_ids])
            segment_ids = torch.tensor([f.segment_ids])
            predictions = self.model(input_ids, segment_ids)
            # confirm we were able to predict 'henson'
            masked_ids = f.mask_ids
            if masked_ids:
                for idx, i in enumerate(masked_ids):
                    predicted_index = torch.argmax(predictions[0, i]).item()
                    predicted_token = self.bert_tokenizer.convert_ids_to_tokens([predicted_index])[0]
                    print('original text is:', f.input_tokens)
                    print('Mask predict is:', predicted_token)
                    corrected_item = predicted_token
        return corrected_item

    def correct(self, sentence=''):
        """
        句子改错
        :param sentence: 句子文本
        :return: 改正后的句子, list(wrong, right, begin_idx, end_idx)
        """
        detail = []
        maybe_errors = self.detect(sentence)
        maybe_errors = sorted(maybe_errors, key=operator.itemgetter(2), reverse=False)
        for item, begin_idx, end_idx, err_type in maybe_errors:
            # 纠错，逐个处理
            before_sent = sentence[:begin_idx]
            after_sent = sentence[end_idx:]

            # 困惑集中指定的词，直接取结果
            if err_type == error_type["confusion"]:
                corrected_item = self.custom_confusion[item]
            elif err_type == error_type["char"]:
                # 对非中文的错字不做处理
                if not is_chinese_string(item):
                    continue
                if not self.check_vocab_has_all_token(sentence):
                    continue
                # 取得所有可能正确的字
                corrected_item = self.bert_lm_infer(sentence, error_begin_idx=begin_idx, error_end_idx=end_idx)
            elif err_type == error_type["word"]:
                corrected_item = item
            else:
                print('not strand error_type')
            # output
            if corrected_item != item:
                sentence = before_sent + corrected_item + after_sent
                detail_word = [item, corrected_item, begin_idx, end_idx]
                detail.append(detail_word)
        detail = sorted(detail, key=operator.itemgetter(2))
        return sentence, detail


if __name__ == "__main__":
    bertCorrector = BertCorrector(config.bert_model_dir,
                                  config.bert_model_vocab,
                                  config.max_seq_length)

    error_sentence_1 = '少先队员因该为老人让座.机七学习是人工智能领遇最能体现智能的一个分知'
    correct_sent = bertCorrector.correct(error_sentence_1)
    print("original sentence:{} => correct sentence:{}".format(error_sentence_1, correct_sent))
