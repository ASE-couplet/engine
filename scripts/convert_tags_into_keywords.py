import json
import random

KEY_WORDS_JSON_PATH = "./rank_key_words.json"

def overlap(tag, keywords):
    for keyword in keywords:
        if keyword in tag or tag in keyword:
            return keyword
    return None

def weak_overlap(tag, keywords):
    for keyword in keywords:
        if set(tag) & set(keyword) != set():
            return keyword
    return None

class TagsProcessor():
    def __init__(self):
        keywords_all = json.load(open(KEY_WORDS_JSON_PATH, 'r', encoding='utf-8'))
        self.keywords = [keyword[0] for keyword in keywords_all]
    def convert_tags_into_keywords(self,tags, n):
        keywords = self.keywords
        result = []
        overlap_result = []
        weak_overlap_result = []
        for tag in tags:
            if tag in keywords:
                result.append(tag)
            else:
                overlap_keyword = overlap(tag, keywords)
                if overlap_keyword is not None:
                    overlap_result.append(overlap_keyword)
                else:
                    weak_overlap = weak_overlap(tag, keywords)
                    if weak_overlap is not None:
                        weak_overlap_result.append(weak_overlap)
        if len(result) >= n:
            return result[:n]
        if len(result) + len(overlap_result) >= n:
            result = result + overlap_result
            return result[:n]
        if len(result) + len(overlap_result) + len(weak_overlap_result) >= n:
            result = result + overlap_result + weak_overlap_result
            return result[:n]
        result = result + overlap_result + weak_overlap_result
        result = result + random.sample(keywords[:500], n - len(result))
        return result

if __name__ == '__main__':
    processor = TagsProcessor()
    result = processor.convert_tags_into_keywords(['加拿大', '枫叶', '猪流感', '奥巴马吗'], 4)
    print(result)