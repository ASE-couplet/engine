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

    tags_str = ""
    for tag in response.json()['description']['tags'][:4]:
        if tags_str == "":
            tags_str = tag
        else:
            tags_str += "，" + tag

    return tags_str

if __name__ == "__main__":
    import ipdb
    ipdb.set_trace()
    image_url =  "https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/" + \
     "Broadway_and_Times_Square_by_night.jpg/450px-Broadway_and_Times_Square_by_night.jpg"
    print(img2tag(image_url))
