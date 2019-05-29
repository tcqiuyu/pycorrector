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
    acc = 0.0
    pbar = tqdm(test_data, desc=str(acc))
    for input, golden in pbar:
        print("{} - {}\t{}".format(pbar.n, input, golden))
        corrected = corrector.correct(input)
        if corrected[0] == golden:
            correct += 1
        acc = correct / total
        pbar.set_description(str(acc))
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
