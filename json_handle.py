import json
from json import JSONDecodeError


# 编写两个函数，一个是储存、一个是读取

def create_userinfo_json(json_str: str, json_path: str):
    # 传入一个字典的字符串, 格式如下
    # '{"job": "Developer", "hobbies": ["reading", "running"]}'
    userinfo = {}
    try:
        with open(json_path, "r") as f:
            userinfo = json.load(f)
    except FileNotFoundError:
        pass
    # 将字典字符串转换为字典对象
    new_dict = json.loads(json_str)

    for key in new_dict.keys():
        if key.isdigit():
            new_dict[key]["login_state"] = "NOKNOW"
            new_dict[key]["PERMISSION"] = "True"
        else:
            return False
    if userinfo == {}:
        userinfo = new_dict
    else:
        # 使用 update() 方法将新字典添加到已有字典中
        userinfo.update(new_dict)
    with open(json_path, "w") as f:
        json.dump(userinfo, f)
    return userinfo


def load_json(json_path: str):
    userinfo = {}
    with open(json_path, "r") as f:
        try:
            userinfo = json.load(f)
        except JSONDecodeError:
            pass
    return userinfo


def update_json(json_path: str, user_id: str, key: str, value: str):
    userinfo = load_json(json_path)
    userinfo[user_id][key] = value
    with open(json_path, "w") as f:
        json.dump(userinfo, f)


def del_json(json_path: str, user_id: str):
    userinfo = load_json(json_path)
    try:
        del userinfo[user_id]
        with open(json_path, "w") as f:
            json.dump(userinfo, f)
        return True
    except KeyError:
        return False


def check_template(json_str):
    try:
        data = json.loads(json_str)
        for key in data:
            result = data[key]
            if isinstance(result, dict) and len(result) == 4:
                if '你的姓名' in result and '你的学号' in result and '是否确保能按时参加会议' in result and '你的班级' in result:
                    return True
    except:
        pass
    return False


#  筛选合适的userinfo，主要通过登录状态和授权状态
def sel_userinfo(json_path: str, login_state=False, permission=True):
    # 只要求许可信息的话就是FT

    userinfo = load_json(json_path)
    keylist = list(userinfo.keys())
  
    if login_state == True and permission == True:
        for key in keylist:
            if userinfo[key]["login_state"] == "True" and userinfo[key]["PERMISSION"] == "True":
                continue
            else:
                del userinfo[key]
        return userinfo

    keylist = list(userinfo.keys())
    if login_state == False and permission == True:
        for key in keylist:
            if userinfo[key]["PERMISSION"] == "True":
                continue
            else:
                del userinfo[key]
        return userinfo
# 用法
# newdict_str = '{"1111111": {"你的姓名": "xxx", "你的学号": "22222222", "是否确保能按时参加会议": "是", "你的班级": "222222"}}'
# save_json(newdict_str,json_path="userinfo.json")
#
# load_json(json_path="userinfo.json")

# info_str1 = r'{"1571823795": {"你的姓名": "吴集星", "你的学号": "2022710466", "是否确保能按时参加会议": "是", "你的班级": "测绘QX221"}}'
# info_str2 = r'{"1476017835": {"你的姓名": "吴集星", "你的学号": "2022710466", "是否确保能按时参加会议": "是", "你的班级": "测绘QX221"}}'
# info_str3 = r'{"2547496916": {"你的姓名": "张子康", "你的学号": "2022710475", "是否确保能按时参加会议": "是", "你的班级": "测绘QX221"}}'
# # info_str = '{"11111": {"你的姓名": "xxx", "你的学号": "33333", "是否确保能按时参加会议": "是", "你的班级": "33333"}}'
# create_userinfo_json(info_str1, json_path="userinfo.json")
# create_userinfo_json(info_str2, json_path="userinfo.json")
# create_userinfo_json(info_str3, json_path="userinfo.json")
# user_info = load_json("userinfo.json")
# print(user_info)
# del_json(json_path="userinfo.json",user_id="11111")
# user_info = load_json("userinfo.json")
# print(user_info)

#
# print(check_template(infostr))
