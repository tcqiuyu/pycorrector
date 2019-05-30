import csv
import time

from tqdm import tqdm
from sklearn import metrics

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
    golden_list, p1_pred, p2_pred = [], [], []
    for input, golden in pbar:
        print("------------------------------------------------------------------")
        print("{} - {}\t{}".format(pbar.n, input, golden))
        assert len(input) == len(golden)
        if len(input) != len(golden):
            continue
        corrected, detail, phase1_golden, phase1_pred, phase2_pred = corrector.correct(input, golden)
        golden_list.extend(phase1_golden)
        p1_pred.extend(phase1_pred)
        p2_pred.extend(phase2_pred)
        if corrected == golden:
            correct += 1
        acc = correct / total
        pbar.set_description(str(acc))

    print("phase1 report:")
    print(metrics.classification_report(golden_list, p1_pred))
    print("")
    print("phase2 report:")
    print(metrics.classification_report(golden_list, p2_pred))
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
