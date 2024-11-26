# youdao_translate.py
import hashlib
import time
import uuid
import requests

import settings

# Youdao API URL and credentials
YOUDAO_URL = 'https://openapi.youdao.com/api'
APP_KEY = settings.YOUDAO_KEY  # Replace with your actual App ID
APP_SECRET = settings.YOUDAO_PASSWORD  # Replace with your actual App Secret
APP_VID = settings.YOUDAO_VID

def encrypt(signStr):
    """Generate SHA-256 hash for the signature"""
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()




def translate(q, from_lang, to_lang):
    """Translate text using Youdao API"""
    data = {}
    data['from'] = from_lang
    data['to'] = to_lang
    data['signType'] = 'v3'
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = APP_KEY + q + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data['appKey'] = APP_KEY
    data['q'] = q
    data['salt'] = salt
    data['sign'] = sign
    data['vocabId'] = APP_VID  # Optional, replace with your vocabulary ID if needed

    # Send the request to the Youdao API
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(YOUDAO_URL, data=data, headers=headers)
    return response.json()  # Return the JSON response


def get_translation(q, from_lang='en', to_lang='zh-CHS'):
    """Convenience function to get translation from Youdao"""
    result = translate(q, from_lang, to_lang)
    if 'translation' in result:
        return result['translation'][0]  # Return the first translation result
    else:
        return "Translation failed"


print(get_translation('Hello Unibear'))