from .config import *
from .submitClass import SubmitClass
from nonebot.plugin import on_keyword, on_command
from nonebot.adapters.onebot.v11 import Bot, Event, MessageEvent, Message
from nonebot.params import CommandArg
from .timer_checker import *
import re
from . import json_handle
import nonebot
import asyncio


async def limit_permission(message_event: MessageEvent):  # 自定义权限，这里指定特定群获取消息
    result = allstring.find(message_event.get_session_id())  # 总模板，只要发送消息的session_id能在被找到,没找到返回-1
    if result == -1: return False
    return True


mtxl = on_keyword(keystring, priority=50, permission=limit_permission)


@mtxl.handle()
async def mtxl_handle(bot: Bot, message_event: MessageEvent):
    text = message_event.get_plaintext()  # 提取消息中的纯文本消息
    pattern = re.compile(rerule)
    txwd_link = re.search(pattern, text).group()  # 从消息中匹配出需要的文本链接

    # 筛选出即登录状态ok又授权了的账号
    mydict2 = json_handle.sel_userinfo(json_path=dir_path + r"\userinfo.json", login_state=True, permission=True)
    # 声明对应submitClass类
    sub = SubmitClass()
    
    nonebot.logger.info("-->mydict2:" + str(mydict2.keys()))
    nonebot.logger.info("-->mydict2:" + str(mydict2))
    nonebot.logger.info("---------------------------------")
    submitResult = sub.submit(str(txwd_link), mydict2)

    for res in submitResult.keys():
        await bot.call_api('send_private_msg', **{
            'user_id': int(res),
            'message': str(txwd_link) + "\n\n" + str(submitResult[res])
        })


# 先授权才能登录
async def user_checker(event: Event) -> bool:
    userid = event.get_user_id()
    userinfo = json_handle.sel_userinfo(json_path=dir_path + r"\userinfo.json", login_state=False, permission=True)
    if userinfo.get(str(userid), False): return True
    return False


txwd_login = on_command(commandstring, rule=user_checker)


@txwd_login.handle()
async def txwd_login(bot: Bot, event: Event):
    user_id = event.get_user_id()  # 字符串变量
    sub = SubmitClass()
    # 首先判断用户是否登录
    state = sub.islogin(user_id, login_Link, waitSecond=2)
    if state == True:  # 这里不写True就会有bug
        # nonebot.logger.info("user_chrome._login1:" + str(state))
        await bot.call_api('send_private_msg', **{
            'user_id': int(user_id),
            'message': "腾讯文档已经是登录状态了，不用登录了"
        })
        json_handle.update_json(dir_path + r"\userinfo.json", user_id, "login_state", "True")
    else:
        # false则说明当前用户并未登录上 调用登录函数
        res = sub.login(user_id, login_Link, True)  
        if res == True:
            imgpath = dir_path + "\\Image\\" + user_id + ".png"
            message = Message(r'[CQ:image,file=file:///' + imgpath + ']')
            await bot.call_api('send_private_msg', **{
                'user_id': int(user_id),
                'message': message
            })
        else:
           # 出现了意外 
           print("Error is login")
           pass
        async def checkUserLogin(sub, user_id,waitSecond=5, repeat=5):
            '''
                该函数用来开启线程任务
            Args:
                sub (SubmitClass): submitclass对象
                username (string): 检测qq号
                waitSecond (int):  浏览器显示等待时间   
                repeat (int): 刷新网页次数
            '''
            if sub.checkUserLogin(driver=sub.logindriver,waitSecond=waitSecond, repeat=repeat) == True:
                await bot.call_api('send_private_msg', **{
                'user_id': int(user_id),
                'message': "腾讯文档登录好了"
                })
                json_handle.update_json(dir_path + r"\userinfo.json", user_id, "login_state", "True")
            else:
                await bot.call_api('send_private_msg', **{
                    'user_id': int(user_id),
                'message': "可能登录上了，也可能没有，再发一次登录指令试试"
                })
                json_handle.update_json(dir_path + r"\userinfo.json", user_id, "login_state", "False")
            # finally 关闭所有的浏览器对象
            sub.quitWebDriver()
        checkFunc = checkUserLogin(sub, user_id, 5, 5)
        # 开启协程
        loop  = asyncio.get_event_loop()
        task = loop.create_task(checkFunc)




# 管理员授权和删除用户的操作
# 管理员授权，更改json文件的对应用户字典的login_state
# 删除用户 删除json中用户字典和浏览器文件
async def manager_permission(event: Event):  # 自定义权限，这里指定特定群获取消息
    if event.get_user_id() == manager_qq:
        return True
    return False


################################### 管理员授权 ##############################
authorize = on_command(("authorize_userinfo",), rule=manager_permission)


@authorize.handle()
async def authorize(bot: Bot, event: Event, args: Message = CommandArg()):
    # 获取命令后面的参数，这里是获取userinfo字典
    # 字典格式如：r'{"157182aa": {"你的姓名": "嘤嘤嘤", "你的学号": "2022710000", "是否确保能按时参加会议": "是", "你的班级": "地质学QX222"}}'
    parameter = args.extract_plain_text()
    # if json_handle.check_template(parameter):
    userinfo = json_handle.create_userinfo_json(parameter, dir_path + r"\userinfo.json")
    if userinfo:
        await bot.call_api('send_private_msg', **{
            'user_id': int(event.get_user_id()),
            'message': "已写入授权和用户信息"
        })
    else:
        await bot.call_api('send_private_msg', **{
            'user_id': int(event.get_user_id()),
            'message': "写入失败,用户信息格式不规范"
        })


################################### 删除用户信息 ##############################

manager_del = on_command(("del_userinfo",), rule=manager_permission)


@manager_del.handle()
async def manager_del(bot: Bot, event: Event, args: Message = CommandArg()):
    parameter = args.extract_plain_text()
    if json_handle.del_json(dir_path + r"\userinfo.json", parameter):

        # 这里还要尝试删除userdata
        import os
        user_chromepath = dir_path + r"\SAVEUSER" + '\\' + parameter
        if os.path.exists(user_chromepath):
            import shutil
            shutil.rmtree(user_chromepath)

        await bot.call_api('send_private_msg', **{
            'user_id': int(event.get_user_id()),
            'message': "已删除" + parameter + "用户信息"
        })
    else:
        await bot.call_api('send_private_msg', **{
            'user_id': int(event.get_user_id()),
            'message': "该用户信息不存在"
        })


################################### 查询所有用户信息 ##############################
manager_search = on_command(("search_alluserinfo",), rule=manager_permission)


@manager_search.handle()
async def manager_search(bot: Bot, event: Event):
    userinfo = json_handle.load_json(dir_path + r"\userinfo.json")

    message = "查询用户信息如下：\n\n"
    for key in userinfo.keys():
        message = message + key + "\n" + str(userinfo[key]) + "\n\n"

    await bot.call_api('send_private_msg', **{
        'user_id': int(event.get_user_id()),
        'message': message
    })

################################### 更新账号登录状态 ##############################
update_login_state = on_command(("update_login_state",), rule=manager_permission)


@update_login_state.handle()
async def update_login_state(bot: Bot, event: Event):


    import nonebot
    nonebot.logger.info("检查腾讯文档登录状态  ")
    
    # 只扫描获取许可的QQ，更新状态
    permission_userinfo = json_handle.sel_userinfo(dir_path + r"\userinfo.json",
                                                   login_state=False, permission=True)

    sub = SubmitClass()

    alluser_list = sub.getAllUserInfo()
    if alluser_list:
        fail_user = []
        for qq_user in alluser_list:

	    

            # 当检查的qquser不是许可用户时，就跳过此次循环
            if not permission_userinfo.get(qq_user, False):
                continue
		
 	    
            nonebot.logger.info("检查腾讯文档登录状态  " + qq_user)

            state = sub.islogin(qq_user, login_Link)
            if state == False:

                json_handle.update_json(dir_path + r"\userinfo.json", qq_user, "login_state", "False")

                fail_user.append(qq_user)
                await bot.call_api('send_private_msg', **{
                    'user_id': int(qq_user),
                    'message': "腾讯文档失效了，请重新发送命令"
                })
                await bot.call_api('send_private_msg', **{
                    'user_id': int(qq_user),
                    'message': "/扫码登录腾讯文档模式,我已登录电脑QQ,随时准备扫描电脑屏幕二维码"
                })
            else:
                json_handle.update_json(dir_path + r"\userinfo.json", qq_user,"login_state", "True")

    userinfo = json_handle.load_json(dir_path + r"\userinfo.json")

    message = "更新后，用户信息如下：\n"
    for key in userinfo.keys():
        message = message + key + "\n" + str(userinfo[key]) + "\n\n"

    await bot.call_api('send_private_msg', **{
        'user_id': int(event.get_user_id()),
        'message': message
    })
