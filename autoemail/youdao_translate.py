# youdao_translate.py
import hashlib
import time
import uuid
import requests

# Youdao API URL and credentials
YOUDAO_URL = 'https://openapi.youdao.com/api'
APP_KEY = '164da688635ff4e7'  # Replace with your actual App ID
APP_SECRET = 'Os4m7CZdKmaMP2cidpP91Q9lvOhmQnN4'  # Replace with your actual App Secret


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
    data['vocabId'] = "0B37D26ECCC84BAB8B058E92D83C0424"  # Optional, replace with your vocabulary ID if needed

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