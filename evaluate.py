import csv
import time

from tqdm import tqdm

from pycorrector import Corrector
from pycorrector.config import common_char_path, same_pinyin_path, same_stroke_path, language_model_path, \
    word_freq_path, custom_confusion_path, place_name_path, person_name_path, \
    stopwords_path, custom_word_freq_path


def load_test_data(path):
    # test_file = "data/sighan bakeroff/test.csv"
    with open(path, "r") as f:
        reader = csv.reader(f)
        test_data = list(reader)
    return test_data


def evaluate(corrector: Corrector, test_data):
    total = len(test_data)
    correct = 0.0
    start_time = time.time()
    for input, golden in tqdm(test_data, desc=correct / total):
        corrected = corrector.correct(input)
        print(corrected)
        if corrected == golden:
            correct += 1
    acc = correct / total
    end_time = time.time()
    return acc, (end_time - start_time)


if __name__ == '__main__':
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
    test_data = load_test_data("data/sighan bakeroff/test.csv")
    print(evaluate(model, test_data))
