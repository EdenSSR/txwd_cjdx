import time
import os
import shutil
import threading
import traceback
import nonebot
from .config import dir_path, question_type_table
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# 引入bot
from nonebot.adapters.onebot.v11 import Bot, Event, MessageEvent, Message


# 最开始的Userdata,每有一个qq号就需要将该文件夹复制到一个新的文件夹中
# USERDATA = "User Data"
# DIRECTORY = "Image"
# SAVEUSERFOLDER = "SAVEUSER"


string_key = ["长江讲坛", "地学之光", "博研论坛"]

USERDATA = os.path.join(dir_path, "User Data")
DIRECTORY = os.path.join(dir_path, "Image")
SAVEUSERFOLDER = os.path.join(dir_path, "SAVEUSER")

# # 修正路径
# os.chdir(dir_path)


class SubmitClass():
    """ 
        只需要完成两个工作，登录与提交
    """
    def __init__(self) -> None:
        # 登录使用的挂载变量
        self.logindriver = None
        # 构建用户全局字典信息，方便后文进程返回消息
        self.allUserInfoDict = None
        # 是否使用未登录时的浏览器控制对象，从而实现在单一用户的情况下尽量少开浏览器
        self.singleUserIsLogin = False
        self.singleUserLoginDriver = None


    def initUserInfo(self, username: str):
        """初始化登录的需要的信息

        Args:
            username (str): 登录的用户qq号
        """
        # 生成两个预备文件夹
        self.checkPrepareFolder()
        # 并且对输入过来的qq号进行一个预先处理
        options = self.generateOptions(username=username)
        return options

    def checkPrepareFolder(self):
        """
            判断准备好的文件夹是否存在
            这个函数只需要在系统启动时 运行一次即可, 每次在调用login时，多加一次检查没啥影响
        """
        if not os.path.exists(DIRECTORY):
            os.makedirs(DIRECTORY)
        if not os.path.exists(SAVEUSERFOLDER):
            os.makedirs(SAVEUSERFOLDER)

    def generateOptions(self, username: str):
        """用于判断当前的qq号是否已经存在了,如果没有，则需要将USERDATA里面的所有文件复制一份

        Args:
            username (str): qq号
        """
        # 生成一个chrome的options
        options = webdriver.ChromeOptions()
        userfolder = SAVEUSERFOLDER+"/"+username
        if not os.path.exists(userfolder):
            # 不存在, 需要将原来的UserData文件夹移动到以该qq命名的文件夹下面
            shutil.copytree(USERDATA, SAVEUSERFOLDER+"\\"+username)
        # 测试, 当不存在文件夹时报错
        assert os.path.exists(userfolder)
        # 构建chrome数据目录，必须使用绝对路径
        # chromeUserData = "user-data-dir="+os.getcwd()+"\\"+SAVEUSERFOLDER + \
        #     "\\"+username

        chromeUserData = "user-data-dir=" + SAVEUSERFOLDER + "\\" + username
        options.add_argument(chromeUserData)
        prefs = {"profile.managed_default_content_settings.images": 0}  # 加载图片
        options.add_experimental_option("prefs", prefs)
        # options.add_argument("--headless")  
        options.add_argument("window-size=1920x1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36")
        options.add_experimental_option("detach", True)
        return options

    def sleep(self, second=0.3):
        """
        用于运行中的暂停
        """
        time.sleep(second)

    def waitElement(self, driver, method, condition,waitSecond=10):
        """用于判断dom元素是否存在

        Args:
            driver (WebDriver): 浏览器对象
            method (EC): 浏览器判断方法
            condition (set): 第一个对象表明元素定位方法,第二个表明条件
            waitSecond (int, optional): Dom元素最大等待时间. Defaults to 10.

        Returns:
            bool: true/存在，false/不存在
        """
        res = True
        try:
            # 默认等待10s
            element = WebDriverWait(driver, waitSecond).until(
                method(condition)
            )
        except (TimeoutException, NoSuchElementException):
            print("Error in ",condition)
            # 如果进入到Except里面，说明查找元素超时
            res = False
        finally:
            return res

    def retryTime(self, driver, method, condition,waitSecond=10, times=3):
        """用于是否失败操作

        Args:
            times (int, optional): 等待最大次数. Defaults to 3.
        """
        deadtime = 0
        while deadtime <= times:
            res = self.waitElement(driver=driver, method=method, condition=condition, waitSecond=waitSecond)
            if res == True:
                return True
            else:
                deadtime += 1
                # 每重试一次都刷新一次页面
                driver.refresh()
        return False

    def saveLoginImg(self, driver, username):
        """用于在未登录的情况获取对应的登录二维码，并且将其保存到对应的DIRECTORY文件夹中，以qq号的形式
        这里获取模拟登录的是https://docs.qq.com/desktop

        """
        # 切换到qq登录框
        res = self.retryTime(driver=driver, method=EC.presence_of_element_located, condition=(By.CLASS_NAME, "qq"), waitSecond=2)
        if res == True:
            driver.find_element(By.CLASS_NAME, "qq").click()
        else:
            # 在重试三次之后任然没有该dom元素，则退出
            # return ("error in loading qq login frame", 10001, False)
            return False
        # 切换对应的frame框
        res = self.retryTime(driver=driver, method=EC.frame_to_be_available_and_switch_to_it, condition=(By.ID, "login_frame"), waitSecond=2)
        if res == False:
            # 失败操作
            # return ("error in switch frame, frame id is login_frame", 10002, False)
            return False
        res = self.retryTime(driver=driver, method=EC.frame_to_be_available_and_switch_to_it, condition=(By.ID, "ptlogin_iframe"), waitSecond=2)
        if res == False:
            # 失败操作
            # return ("error in switch frame, frame id is ptlogin_iframe", 10002, False)
            return False
        # 获取对应的登录二维码
        res = self.retryTime(driver=driver, method=EC.presence_of_element_located, condition=(By.ID, 'qr_area'), waitSecond=2)
        if res == False:
            # return ("error in qq login image, image id is qr_area", 10003, False)
            return False
        imgcode = driver.find_element(By.ID, 'qr_area')
        # 直接按照对应的qq号进行存储
        filename = DIRECTORY+"/"+username+".png"
        nonebot.logger.info("write image to" + filename)
        if imgcode:
            # self._driver.get_screenshot_as_file(filename=filename)
            nonebot.logger.info("write success")
            imgcode.screenshot(filename)
            # return ("write success qq image", 200, True)
            return True


    def login(self, username: str, url: str, needImg=False):
        """登录

        Args:
            url (str): 模拟登录的腾讯文档url
            username (str): 登录的用户qq号
            needImg (bool): 是否需要登录的二维码
        """
        # 这里先判断是否存在单用户使用的浏览器对象
        if self.singleUserIsLogin is True and self.singleUserLoginDriver is not None:
            # 存在，说明是未登录, 并且已经提前使用过islogin函数去调用,这里就不用在开启浏览器
            self.logindriver = self.singleUserLoginDriver
        else:
            # 获取对应的登录专用options
            options = self.generateOptions(username)
            # 将登录的浏览器控制权挂载到类变量下
            self.logindriver = webdriver.Chrome(options=options)  # 打开浏览器
            self.logindriver.get(url)
        # 保存图片
        msg, code, res = self.saveLoginImg(self.logindriver, username)
        nonebot.logger.info(msg)
        return res

    def quitWebDriver(self):
        """
            用于释放所有的浏览器对象
        """
        if self.singleUserLoginDriver is not None and self.singleUserIsLogin is False:
            # 表示单用户浏览器对象不需要的时候
            self.singleUserLoginDriver.quit()
        if self.logindriver is not None:
            self.logindriver.quit()

    def islogin(self, username, url, driver=None, waitSecond=10):
        """用于判断当前用户是否登录

        Args:
            username: string qq号
            url: string 登录链接
            driver: Webdriver.Chrome 开启的浏览器对象
            waitSecond: int 浏览器显示等待时间
        Returns:
            bool: 是否登录了
        """
        if driver == None:
            # 如果driver是None对象，说明当前需要开启浏览器去访问
            options = self.generateOptions(username)
            driver = webdriver.Chrome(options=options)
            driver.get(url)
        # 不为空，直接使用传入进行来的driver即可
        res = self.waitElement(driver, EC.presence_of_element_located, (By.ID, "account-avatar-container"), waitSecond=waitSecond)
        # 这里说明并没有检查到登录对象， 可以将未登录使用的driver对象保留下来，方便后续使用
        if res == False:
            # 表示可以使用单用户登录driver
            self.singleUserIsLogin = True
            self.singleUserLoginDriver = driver
        else:
            # 说明用户已经登录, 将浏览器对象释放
            driver.quit()
        return res

    def getAllUserInfo(self):
        """遍历所有的SAVEUSER下面存在的用户信息

        """
        allUserInfo = []
        for filename in os.listdir(SAVEUSERFOLDER):
            allUserInfo.append(filename)
        return allUserInfo

    def submit(self, url: str, mydict: dict):
        """提交动作
        Args:
            url: 表单链接
            mydict: 所有的用户信息
        """
        # 获取所有的用户信息
        allUserInfo = list(mydict.keys())
        # 并且为这所有的用户构建一个全局字典
        self.allUserInfoDict = {}
        for user in allUserInfo:
            self.allUserInfoDict[user] = False
        print(allUserInfo)
        # 另外，能在SAVEUSER里面的都是已经登录过的qq
        threads = []  # 定义一个线程池
	##################
        nonebot.logger.info("###############################")
        nonebot.logger.info("allUserInfo:"+str(allUserInfo))
        nonebot.logger.info("mydict:"+str(mydict.keys()))
        for user in allUserInfo:
            threads.append(threading.Thread(
                target=self.singleSubmit, args=(user, url, mydict[user])))

        for t in threads:
            t.start()
        # 卡住主线程
        for t in threads:
            t.join()
        print("全部执行完毕")
        # 此时，对应的用户提交信息全部记录在self.allUserInfoDict中
        for userinfo in self.allUserInfoDict.keys():
            if self.allUserInfoDict[userinfo]:
                print(userinfo, "submit")
            else:
                print(userinfo, "no submit")
        return self.allUserInfoDict

    # 适配下新版的收集表
    def singleSubmit(self, userinfo: str, url: str, mydict: dict):
        """构建单个用户options

        Args:
            userinfo (str): 用户qq号
            url (str): 访问的url
            mydict (dict): 提交的用户信息
        """
        # 构建对应的UserData位置
        # chromeUserData = "user-data-dir="+os.getcwd()+"\\"+SAVEUSERFOLDER + \
        #     "\\"+userinfo
        options = self.generateOptions(userinfo)  # 生成用户的options
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        try:
            driver.find_element(By.CLASS_NAME, "user-info-wrap")
        except NoSuchElementException:
            print("该账号未登录")
            driver.quit()
            return False
        else:

            try:
                # 模仿用户输入关键字
                text = driver.find_element(By.XPATH, "//*[contains(text(),'会议')]").text
                nonebot.logger.info("text:" + text)
            except NoSuchElementException:
                nonebot.logger.info("#######非会议的#######")
                return False

            # 登录的情况下，执行
            # 填写表单
            try:

                elements = driver.find_elements(
                    By.XPATH, "//span[@class='form-auto-ellipsis']")
                for index in range(len(elements)):
                    element = driver.find_elements(By.XPATH, "//span[@class='form-auto-ellipsis']")[index]
                    span_text = element.text
                    question_type = question_type_table.get(span_text)

                    # 当问题不是选择类型
                    if question_type == "input":

                        node = driver.find_elements(By.TAG_NAME, 'textarea')[index]

                        # 修改div[class = form-simple-main form-ui-component-basic size-small multiple with-border]
                        parent_div = node.find_element(By.XPATH, '../..')
                        driver.execute_script("arguments[0].classList.add('focus');", parent_div)
                        if mydict.get(span_text) is not None:
                            node.send_keys(mydict[span_text])
                        else:
                            node.send_keys(" ")
                        driver.execute_script("arguments[0].classList.remove('focus');", parent_div)

                    elif question_type == "click":
                        text_choice = mydict.get(span_text)

                        element_xpath = "//span[text()='" + text_choice + "']"
                        element_needClick = element.find_element(By.XPATH, element_xpath)
                        driver.execute_script("arguments[0].click();", element_needClick)
                # time.sleep(0.2)
                driver.execute_script("arguments[0].click();", driver.find_element(
                    By.XPATH, '//button[text()="提交"]'))
                time.sleep(0.1)
                driver.execute_script("arguments[0].click();", driver.find_element(
                    By.XPATH, '//div[text()="确认"]'))
                self._sleep(0.1)  # 等待1s
                driver.quit()
                self.allUserInfoDict[userinfo] = True
                return True
            except Exception as E:
                traceback.print_exc()
                return False

    def returnMsg(self, msg, code):
        """用于提示信息, 暂时没用

        Args:
            msg (string): 错误信息
            code (int): 错误代码
        """
        return (msg, code)

    def checkUserLogin(self, driver=None, waitSecond=10, repeat=3):
        """用于检测用户是否扫码登录没有, 并且经过waitSecond时间之后，默认返回失败

        Args:
            driver (WebDriver): 浏览器对象
            waitSecond (int, optional): 每一次检测持续时间
            repeat (int, optional): 重复次数

        Returns:
            bool: true/表示扫码成功，false表示超时
        """
        return self.retryTime(driver, EC.presence_of_element_located,(By.ID, "account-avatar-container"), waitSecond=waitSecond)
