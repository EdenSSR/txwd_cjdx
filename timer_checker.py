from nonebot import require, get_bots

from . import json_handle
from .config import *

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler
from .submitClass import SubmitClass


# https://docs.qq.com/desktop 这是腾讯文档的网址
@scheduler.scheduled_job("cron", hour="*/8", id="job_0")
async def run_every_2_hour():
    bot, = get_bots().values()

    await bot.call_api('send_private_msg', **{
        'user_id': int(manager_qq),
        'message': "开始检测已经获得许可的账号状态"
    })

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

            state = sub.login(qq_user, login_Link)
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
                json_handle.update_json(dir_path + r"\userinfo.json", qq_user, "login_state", "True")

        await bot.call_api('send_private_msg', **{
            'user_id': int(manager_qq),
            'message': "fail_user" + str(fail_user)
        })
