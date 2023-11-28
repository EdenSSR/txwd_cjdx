# #########################此处可修改###########################


# 这里用小京东1571823795进行测试，监控1476017835
# submit_qq = "1571823795"  # 这里填写nonebot已经登录的qq，这里的，用来提交腾讯文档
qq_groups = ["616172750", "655188278" , "643920453" ]  # 监控的qq群 643920453
qq_groups_user = ["2284850907", "1571823795", "2547496916", "1395169049"]  # 指定qq群的人

keystring = {"地学之光第", "长江讲坛第", "讲座将在会后发放凭证"}

rerule = "https://docs.qq.com/form/page/[A-Za-z0-9]{10,20}"

# notify_qqs = ["1571823795", "2547496916"]  # task完成后所通知的qq

dirpath = ""  # 这里填相对路径 os获取绝对路径，加上相对

mydict = {"userid": {'你的姓名': "xxx", '你的学号': '22222222', '是否确保能按时参加会议': '是', '你的班级': '222222'},
          "1476017835": {'你的姓名': "吴集星", '你的学号': '2022710466', '是否确保能按时参加会议': '是',
                         '你的班级': '测绘QX221'},
          "2547496916": {'你的姓名': "张子康", '你的学号': '2022710475', '是否确保能按时参加会议': '是',
                         '你的班级': '测绘QX221'},
          }

commandstring = ("扫码登录腾讯文档模式,我已登录电脑QQ,随时准备扫描电脑屏幕二维码",)

license_qq = ["1571823795", "1476017835", "2547496916"]  # 获得许可的qq
manager_qq = "1571823795"
# #########################此处以下不可修改########################
# 字符预处理 以下不要修改

allstring = ""  # group_{self.group_id}_{self.user_id}
for str1 in qq_groups:
    for str2 in qq_groups_user:  allstring = allstring + "group_" + str1 + "_" + str2 + '/'

login_Link = "https://docs.qq.com/desktop"

import os

dir_path = os.getcwd() + r"\src\plugins\txwd_sub"

# 张子康的参数
SucessMsg = {
    "code": "10000",
    "msg": None
}

TimeoutErrorMsg = {
    "code": "10001",
    "msg": "网络出现问题"
}
ElementNotFoundErrorMsg = {
    "code": "10002",
    "msg": "当前页面上并没有找到对应的元素"
}

ExceptionErrorMsg = {
    "code": "50001",
    "msg": "发生其他异常"
}
