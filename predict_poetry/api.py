# -*- coding: utf-8 -*-
import requests
import json

from io import BytesIO

def img2tag(image_url):
    """
    :param image_url: Set image_url to the URL of an image that you want to analyze.
    :return analysis: The 'analysis' object contains various fields that describe the image. 
    The most relevant caption for the image is obtained from the 'description' property.
    """

    subscription_key = "d6b5c62ea5d140eda8ad3dd2b52be86e"
    assert subscription_key

    # You must use the same region in your REST call as you used to get your
    # subscription keys. For example, if you got your subscription keys from
    # westus, replace "westcentralus" in the URI below with "westus".
    #
    # Free trial subscription keys are generated in the westcentralus region.
    # If you use a free trial subscription key, you shouldn't need to change
    # this region.
    vision_base_url = "https://westcentralus.api.cognitive.microsoft.com/vision/v2.0/"

    analyze_url = vision_base_url + "analyze"


    headers = {'Ocp-Apim-Subscription-Key': subscription_key }
    params  = {'visualFeatures': 'Categories,Description,Color',
                'language': 'zh'}
    data    = {'url': image_url}
    response = requests.post(analyze_url, headers=headers, params=params, json=data)
    response.raise_for_status()

    # The 'analysis' object contains various fields that describe the image. The most
    # relevant caption for the image is obtained from the 'description' property.
    analysis = response.json()

    filter_neg_tags = ['室外', '游戏机', '室内','眼镜', '户外', '抽象', '自然', '空气']

    tags_convert_dict = {'年轻':'人', '公寓':'屋', '桌子': '柜', '柜台':'柜', '橙子':'果',
                         '穿着':'衣', '星星':'星', '峡谷':'峡'}

    tags_str = ""
    tags = response.json()['description']['tags']
    filtered_tags = []
    for tag in tags:
        if tag not in filter_neg_tags:
            if tag in tags_convert_dict.keys():
                filtered_tags.append(tags_convert_dict[tag])
            else:
                filtered_tags.append(tag)

    for tag in filtered_tags[:4]:
        if tags_str == "":
            tags_str = tag
        else:
            tags_str += "，" + tag

    return tags_str

if __name__ == "__main__":
    image_url =  "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/" + \
     "Broadway_and_Times_Square_by_night.jpg/450px-Broadway_and_Times_Square_by_night.jpg"
    print(img2tag(image_url))