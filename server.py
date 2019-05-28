import argparse
import json

from flask import Flask, request

from address_corrector import AddressCorrector
from pycorrector import Corrector
from pycorrector.config import *


def start_main_server():
    app = Flask(__name__)

    general_corrector = Corrector(common_char_path=common_char_path,
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
    address_corrector = AddressCorrector()

    @app.route('/text_correction', methods=['POST'])
    def correct():
        text_json = json.loads(request.data.decode('utf-8'), strict=False)
        to_correct = text_json['text']
        area = text_json['area']
        if area == "address":
            condition_address = text_json['condition']
            print(to_correct)
            print(condition_address)
            corrected_text = address_corrector.correct(to_correct, condition_address)
            ret = {
                "corrected_text": corrected_text,
                "ret_code": 1
            }
        else:
            corrected_text = general_corrector.correct(to_correct)
            ret = {
                "corrected_text": corrected_text,
                "ret_code": 1
            }
        return json.dumps(ret)

    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="文本纠错模型 copyright by GammaLab@金融壹账通")

    parser.add_argument('port', default=9140, type=int, help='服务端口，默认9130')
    args = parser.parse_args()

    start_main_server().run(host='0.0.0.0', port=args.port)
