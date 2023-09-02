import xml.dom.minidom
from xml.dom.minidom import parse
import time
import requests
import openai
import os

apikey_fn = "./apikey.txt"
if os.path.exists(apikey_fn):
    with open(apikey_fn, 'rt', encoding='utf-8') as f:
        openai.api_key = f.readline().strip()
else:
    openai.api_key = "sk-"

# 需要对比测试FineTune和不FT的结果？
# openai.error.InvalidRequestError: 'messages' is a required property
    # "choices": [
    #     {
    #         "message": {
    #             "role": "assistant",
    #             "content": "起草一封电子邮件或其他写作材料。"
    #         },
    #         "finish_reason": "stop",
    #         "index": 0
    #     }
    # ]
def CalChatCompletion(text, model, temperature=0.5, frequency_penalty=0.0):
    try:
        response = openai.ChatCompletion.create(
            model=model,  # 'ft:gpt-3.5-turbo-0613:personal::7u077XVx' 'text-davinci-003',
            #prompt=text,    #   prompt="Translate this into English,\n" + text + "\n",
            messages=[
                {"role": "system", "content": "你是一个中英文翻译器。"},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("CalChatCompletion", e)
    finally:
        return ""

# 对话模型
def CallCompletion(text,model='text-davinci-003'):
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="Translate this into English, " +text+"\n",
            temperature=0.3,
            max_tokens=500,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print("CallCompletion", e)
    finally:
        return ""

# "text-davinci-003"
# ft模型该如何call的语法?
def CallTranslates(text):
    return CalChatCompletion(text, model='ft:gpt-3.5-turbo-0613:personal::7u077XVx', temperature=0.3)    #"text-davinci-003",

# http://hf.co上架设的一个免费Google的API
def translate(text, lan, tolan):
    dta = requests.post(
        "http://api.fanyi.baidu.com/api/trans/vip/translate?q=" + text + "&from=" + lan + "&to=" + tolan +
        "&appid=2015063000000001&salt=1435660288&sign=f89f9594663708c1605f3d736d01d2d4").json()
    return "test";
    # return requests.post("https://hf.space/embed/mikeee/gradio-gtr/+/api/predict", json={"data": [text, lan, tolan]}).json()["data"][0]



def loadXml(path):
    print('Test LoadXML:' + path)
    domTree = parse(path)
    rootnode = domTree.documentElement
    # print(rootnode.toxml())
    dic = {}
    records = rootnode.getElementsByTagName('record')
    print(len(records))
    for i in range(len(records)):
        fields = records[i].getElementsByTagName('field')
        key = "null"
        for j in range(len(fields)):
            if (fields[j].getAttribute('name') == 'sLanguageIndex'):
                tranText = fields[j].childNodes[0].data
                key = tranText
            if (fields[j].getAttribute('name') == 'sText' and key != "null"):
                tranText = fields[j].childNodes[0].data
                dic[key] = tranText
                # print(key +" : "+tranText)
    return dic


def loadXml2(path):
    print('Test loadXml2:' + path)
    domTree = parse(path)
    rootnode = domTree.documentElement
    dic = {}
    records = rootnode.getElementsByTagName('record')
    print(len(records))
    for i in range(len(records)):
        fields = records[i].getElementsByTagName('field')
        key = "null"
        for j in range(len(fields)):
            if (fields[j].getAttribute('name') == 'sLanguageIndex'):
                tranText = fields[j].childNodes[0].data
                key = tranText
            if (fields[j].getAttribute('name') == 'sText'):
                tranText = fields[j].childNodes[0].data
                key = tranText
            if (fields[j].getAttribute('name') == 'sFlag' and key != "null"):
                tranText = fields[j].childNodes[0].data
                dic[key] = tranText
                # print(key +" : "+tranText)
    return dic

#
def SaveToXml(dic, dic2, filename):
    doc = xml.dom.minidom.Document();
    root = doc.createElement('data')
    doc.appendChild(root)
    for var in dic:
        str = dic.get(var);
        recordroot = doc.createElement('record')
        fieldroot = doc.createElement("field")
        fieldroot.setAttribute("name", 'sLanguageIndex')
        fieldroot.setAttribute("classT", "string")
        fieldroot.appendChild(doc.createTextNode(var))
        recordroot.appendChild(fieldroot)

        fieldroot = doc.createElement("field")
        fieldroot.setAttribute("name", 'sText')
        fieldroot.setAttribute("classT", "string")
        fieldroot.appendChild(doc.createTextNode(dic.get(var)))
        recordroot.appendChild(fieldroot)

        fieldroot = doc.createElement("field")
        fieldroot.setAttribute("name", 'sFlag')
        fieldroot.setAttribute("classT", "string")
        fieldroot.appendChild(doc.createTextNode(dic2[var]))
        recordroot.appendChild(fieldroot)

        root.appendChild(recordroot)

    with open('./' + filename, 'w', encoding='utf-8') as fp:
        doc.writexml(fp, indent='', addindent='\t', newl='\n', encoding='utf-8')
        fp.close()
    print("Save OK")


# dic: 原始字典
# dic2: no use
# filename:保存文件
def translateDic(dic, dic2, filename, lan, tolan):
    # "zh", "en"
    # zh-hans zh-hant
    dic2 = {}
    codeCnt = 0;
    for var in dic:
        dic2[var] = "0"
    diccopy = {}
    for var in dic:
        retStr = translate(dic.get(var), lan, tolan)
        codeCnt = codeCnt + 1
        diccopy[var] = retStr;
        dic2[var] = "1"
        print(var + " : " + retStr)
        if (codeCnt % 20 == 0):
            SaveToXml(diccopy, dic2, filename)
    SaveToXml(diccopy, dic2, filename)


if __name__ == '__main__':
    # while True:
    #    text = input("小主：")
    #    print('AI:', CallAI(text))
    # mode = input("功能选项：1.问答 2.翻译 \n请输入：")
    # if mode == "1" :
    #         while True:
    #            text=input(Fore.RED+"小主：")
    #            print(Fore.GREEN+'AI:',Fore.GREEN+CallAI(text))
    # elif mode == "2":
    #         while True:
    #            text=input(Fore.RED+"小主：")
    #            print(Fore.GREEN+'AI:',Fore.GREEN+CallTranslates(text))
    # else:
    #         # 翻译环境

    # 检查openai ft模型:

    # 如何使用ft模型
#    t =CalChatCompletion("他认识很多人。", model='ft:gpt-3.5-turbo-0613:personal::7u077XVx')   # He knows a lot of people.
#    t =CalChatCompletion("如何选择单位", model='ft:gpt-3.5-turbo-0613:personal::7u077XVx')    #"How to select a channel is not obvious."

    text = "光标放在指定单位或建筑，再点击选择键选择该单位或建筑"
    t =CalChatCompletion(text, model='ft:gpt-3.5-turbo-0613:personal::7u077XVx')    #'Move the cursor to the unit you want to use, and press the left button.'
    # 使用text模型:
    #t =CallCompletion(text, model='text-davinci-003')   # '\nPlace the cursor on the designated unit or building, then click the select key to select the unit or building.'
    print(t)

    # dic = loadXml("D:/Work/ZR_4/Zhurong/Assets/Export/Map/map_101/config/config_xml/MultipleLanguage_cn.xml")
    # dic2 = {} #loadXml2("D:/Std/pythonProject1/Ch_Hant.xml")
    # # translateDic(dic,'Ch_En.xml','ch','en')
    # translateDic(dic, dic2, 'Ch_Hant.xml', 'zh-hans', 'zh-hant')

    pass
# input("结束")
