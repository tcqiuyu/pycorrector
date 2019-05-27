import re

import Levenshtein as leven
from pypinyin import pinyin, Style

import config
from detector import Detector
from utils.cpca import transform, province_map


def reverse_dict_with_not_unique_value(dic: dict):
    ret = {}
    for key in dic:
        val = dic[key]
        if val not in ret:
            ret[val] = [key]
        else:
            ret[val].append(key)
    return ret


province_all_aliases = reverse_dict_with_not_unique_value(province_map)


class AddressCorrector(Detector):

    def __init__(self):
        super(AddressCorrector, self).__init__()
        self.name = 'address_corrector'
        self.initialized_detector = False

    def initialize_detector(self):
        self.initialized_detector = True

    def correct(self, sentence_to_correct: str, condition_address: str, threshold=10):
        possible_right_list, need_to_check_list, _ = AddressCorrector._get_possible_parts(condition_address)

        possible_right_map = {}
        for item in possible_right_list:
            if len(item) in possible_right_map:
                possible_right_map[len(item)].append(item)
            else:
                possible_right_map[len(item)] = [item]

        distances_result = []
        for window_size in possible_right_map.keys():
            words_to_detect = possible_right_map[window_size]
            for i in range(len(sentence_to_correct)):  # 划窗
                if i + window_size >= len(sentence_to_correct):
                    break
                running_word = sentence_to_correct[i: i + window_size]
                sentence_before = sentence_to_correct[:i]
                sentence_after = sentence_to_correct[i + window_size]
                running_word_pinyins = pinyin(running_word, style=Style.TONE3)
                for word_to_detect in words_to_detect:  # 检测与相同长度不同备选词编辑距离
                    assert len(word_to_detect) == len(running_word)
                    pinyins_to_detect = pinyin(word_to_detect, style=Style.TONE3)
                    dist = 0.0
                    for running_py, to_detect_py in zip(running_word_pinyins, pinyins_to_detect):
                        # 计算编辑距离
                        edit_distance = leven.distance(to_detect_py[0], running_py[0])
                        """检测发音相似度"""
                        if edit_distance >= len(to_detect_py):
                            edit_distance = edit_distance  # 若全部都不一样，则添加penalty
                        dist += edit_distance
                    """检测字相似度"""
                    dist_2 = leven.distance(word_to_detect, running_word) * 3
                    dist += dist_2
                    if dist < threshold:
                        # 距离，原句，改正句
                        distances_result.append(
                            (dist, sentence_to_correct, sentence_before + word_to_detect + sentence_after,
                             (i, i + window_size), running_word, word_to_detect))
        distances_result.sort(key=lambda x: x[0])

        # for window_size in range(1, len(sentence_to_correct) + 1):
        #     for i in range(len(sentence_to_correct)):  # 划窗
        #         if i + window_size > len(sentence_to_correct):
        #             break
        #         running_word = sentence_to_correct[i: i + window_size]
        #
        #         sentence_before = sentence_to_correct[:i]
        #         sentence_after = sentence_to_correct[i + window_size:]
        #         for word_to_detect in possible_right_list:  # 检测与相同长度不同备选词编辑距离
        #             running_word_pinyins = pinyin(running_word, style=Style.TONE3)
        #             pinyins_to_detect = pinyin(word_to_detect, style=Style.TONE3)
        #             dist = 0.0
        #             # 解决running word 和 word to detect 长度不等的情况
        #             diff = abs(len(running_word_pinyins) - len(pinyins_to_detect))
        #             if len(running_word_pinyins) > len(pinyins_to_detect):
        #                 pinyins_to_detect = pinyins_to_detect + [[""]] * diff
        #             else:
        #                 running_word_pinyins = running_word_pinyins + [[""]] * diff
        #
        #             """检测发音相似度"""
        #             for running_py, to_detect_py in zip(running_word_pinyins, pinyins_to_detect):
        #                 # 计算编辑距离
        #                 edit_distance = leven.distance("".join(to_detect_py), "".join(running_py))
        #                 if edit_distance >= len(to_detect_py):
        #                     edit_distance = edit_distance  # 若全部都不一样，则添加penalty
        #                 dist += edit_distance
        #             """检测字相似度"""
        #             dist_2 = leven.distance(word_to_detect, running_word) * 3
        #             dist += dist_2
        #             if dist <= threshold:
        #                 # 距离，原句，改正句
        #                 distances_result.append(
        #                     (dist, sentence_to_correct, sentence_before + word_to_detect + sentence_after,
        #                      (i, i + window_size), running_word, word_to_detect))
        # distances_result.sort(key=lambda x: x[0])

        # output minimum distance with no overlap
        correct_overlap = set()
        for distance_item in distances_result:
            if not correct_overlap.intersection(set(range(*distance_item[3]))):  # 如果没有overlap且最小distance，则添加
                sentence_to_correct = sentence_to_correct.replace(distance_item[-2], distance_item[-1])
                correct_overlap = correct_overlap.union(set(range(*distance_item[3])))

        return sentence_to_correct

    @staticmethod
    def _get_possible_parts(address: str):
        condition_data = transform([address], cut=False)
        condition_province, condition_city, condition_area, condition_addr = condition_data.iloc[0]
        """可以纠正的信息"""
        possible_right_parts = []
        """基本是多少号多少楼这种信息"""
        need_to_check_parts = []

        """分割结果"""
        split = [condition_province, condition_city, condition_area]
        # split = [condition_province, condition_city, condition_area]
        if condition_province != "":
            possible_right_parts.extend(province_all_aliases[condition_province])
        if condition_city != "":
            possible_right_parts.append(condition_city)
        if condition_area != "":
            possible_right_parts.append(condition_area)
        if condition_city.endswith("市"):
            possible_right_parts.append(condition_city[:-1])
        if condition_city.endswith("特别行政区"):  # 香港，澳门
            possible_right_parts.append(condition_city[:-5])
        if condition_area.endswith("市") or condition_area.endswith("区"):
            possible_right_parts.append(condition_area[:-1])

        condition_addr_list, special_parts = AddressCorrector._split_address(condition_addr)
        split.extend(condition_addr_list)
        split.extend(special_parts)
        """添加可能的别名，例如XX路/小区->XX"""
        for additional_addr_part in condition_addr_list:
            if re.fullmatch(".+?(路|((?<!小)区)|((?<!大)街(?!道)))", additional_addr_part):
                possible_right_parts.append(additional_addr_part[:-1])
                possible_right_parts.append(additional_addr_part)
            elif re.fullmatch(".+?(小区|大街|街道)", additional_addr_part):
                possible_right_parts.append(additional_addr_part[:-2])
                possible_right_parts.append(additional_addr_part)
            elif re.match('([\\d一二三四五六七八九十百千]+?(?:栋|幢|号))|'  # XX号XX栋XX号楼，不完全匹配防止corner case
                          '([\\d一二三四五六七八九十百千]+?[层室])|', additional_addr_part):
                need_to_check_parts.append(additional_addr_part)
                need_to_check_parts.append(additional_addr_part[:-1])

        for special_part in special_parts:
            possible_right_parts.append(special_part)
        return possible_right_parts, need_to_check_parts, split

    @staticmethod
    def _split_address(address: str):
        """bad case: 德路景小区"""
        pat = re.compile('(.+?(?:区|路|(?:街道?)|(?:号(?!楼|院))))|'
                         '([\\d一二三四五六七八九十百千A-Z]+?(?:座|栋|幢|号楼|号院))|'
                         '([\\d一二三四五六七八九十百千A-Z]+?[楼层室])|'
                         '(.+?)')
        matched = pat.findall(address)
        ret = []

        running_str = ""
        special_part = []
        for i in range(len(matched)):
            one_district_road_num, one_building, one_room, one_other = matched[i]
            if one_district_road_num != "":
                ret.append(one_district_road_num)
            if one_building != "":
                ret.append(one_building)
            if one_room != "":
                ret.append(one_room)

            if one_other != "":
                running_str = running_str + one_other
            else:
                if running_str != "":
                    special_part.append(running_str)
                    running_str = ""
                else:
                    continue
        if running_str != "":
            special_part.append(running_str)
        return ret, special_part


if __name__ == '__main__':
    address_corrector = AddressCorrector(config.language_model_path)
    # zhuxin
    # zhejiang
    print(address_corrector.correct("我住新城花园", "浙江省诸暨市暨阳街道市南路85号兴城花园10幢010502"))
    # print(address_corrector._get_possible_parts("辽宁省北通市后门区幸福花园15号楼101室")[2])
    # address_corrector.correct("", "广东省东莞市虎门镇大宁社区浦江路2号")
    # with open("../data/地址数据/addr.csv", "r") as f:
    #     with open("../data/地址数据/addr_parse.txt", "w") as fin:
    #         for line in tqdm(f.readlines()):
    #             addr = line.split(',')[0]
    #             if addr == "":
    #                 continue
    #             fin.write(addr + "\n")
    #             _, _, split = address_corrector._get_possible_parts(addr)
    #             fin.write(str(split) + "\n")
