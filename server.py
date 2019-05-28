import argparse
import json

from flask import Flask, request

from address_corrector import AddressCorrector


def start_main_server():
    app = Flask(__name__)

    address_corrector = AddressCorrector()

    @app.route('/correct_text', methods=['POST'])
    def correct():
        text_json = json.loads(request.data.decode('utf-8'), strict=False)
        to_correct = text_json['text']
        area = text_json['area']
        if area == "address":
            condition_address = text_json['condition']
            corrected_text = address_corrector.correct(to_correct, condition_address)
            ret = {
                "corrected_text": corrected_text,
                "ret_code": 1
            }
            return json.dumps(ret)
        else:
            raise NotImplementedError

    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="文本纠错模型 copyright by GammaLab@金融壹账通")

    parser.add_argument('port', default=9140, type=int, help='服务端口，默认9130')
    args = parser.parse_args()

    start_main_server().run(host='0.0.0.0', port=args.port)
