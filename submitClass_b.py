import time
import os
import shutil
import threading
import traceback
import nonebot
from .config import dir_path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 最开始的Userdata,每有一个qq号就需要将该文件夹复制到一个新的文件夹中
# USERDATA = "User Data"
# DIRECTORY = "Image"
# SAVEUSERFOLDER = "SAVEUSER"

USERDATA = os.path.join(dir_path, "User Data")
DIRECTORY = os.path.join(dir_path, "Image")
SAVEUSERFOLDER = os.path.join(dir_path, "SAVEUSER")

# # 修正路径
# os.chdir(dir_path)


class SubmitClass():
    def __init__(self) -> None:
        self.driver = None
        # 构建用户全局字典信息，方便后文进程返回消息
        self.allUserInfoDict = None

    def _initUserInfo(self, username: str):
        """初始化登录的需要的信息

        Args:
            username (str): 登录的用户qq号
        """
        # 生成两个预备文件夹
        self._checkPrepareFolder()
        # 并且对输入过来的qq号进行一个预先处理
        options = self._generateOptions(username=username)
        return options

    def _checkPrepareFolder(self):
        """判断准备好的文件夹是否存在
        """
        if not os.path.exists(DIRECTORY):
            os.makedirs(DIRECTORY)
        if not os.path.exists(SAVEUSERFOLDER):
            os.makedirs(SAVEUSERFOLDER)

    def _generateOptions(self, username: str):
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
        options.add_argument("--headless")
        options.add_argument("window-size=1920x1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36")
        options.add_experimental_option("detach", True)
        return options

    def _sleep(self, second=0.3):
        """
        用于运行中的暂停
        """
        time.sleep(second)

    def _saveLoginImg(self, driver, username):
        """用于在未登录的情况获取对应的登录二维码，并且将其保存到对应的DIRECTORY文件夹中，以qq号的形式
        这里获取模拟登录的是https://docs.qq.com/desktop

        """
        # 等待一会
        self._sleep()
        # 切换到qq登录框
        driver.find_element(By.CLASS_NAME, "qq").click()
        self._sleep()
        # 切换到对应的iframe中
        frame = driver.find_element(By.ID, "login_frame")
        driver.switch_to.frame(frame)
        self._sleep(0.5)
        # 获取对应的登录二维码
        imgcode = driver.find_element(By.ID, 'qr_area')
        # 直接按照对应的qq号进行存储
        filename = DIRECTORY+"/"+username+".png"
        nonebot.logger.info("write image to" + filename)
        if imgcode:
            # self._driver.get_screenshot_as_file(filename=filename)
            nonebot.logger.info("write success")
            imgcode.screenshot(filename)

    def login(self, username: str, url: str, needImg=False):
        """登录

        Args:
            url (str): 模拟登录的腾讯文档url
            username (str): 登录的用户qq号
            needImg (bool): 是否需要登录的二维码
        """
        # 获取对应的options
        options = self._initUserInfo(username)
        self.driver = webdriver.Chrome(options=options)  # 打开浏览器
        self.driver.get(url)
        # 等待
        self._sleep(1)

        if needImg==False: self._sleep(4)

        user_elements = self.driver.find_elements(By.ID, "account-avatar-container")
        nonebot.logger.info("\n" + "#" * 30 + "len(user_elements):" +
                            str(len(user_elements)) + "#" * 30 + "\n")
        if len(user_elements) == 1:
            self.driver.quit()
            return True
        # 当没有检测到该元素的时候，说明并没有登录,需要保存对应的二维码用于登录
        else:
            if not needImg:
                self.driver.quit()
                return False
            else:
                self._saveLoginImg(self.driver, username)
                # self._driver.quit()
                return False

    def delay_quit(self, delay=0.5):
        time.sleep(delay)
        self.driver.quit()

    def islogin(self):
        try:
            element = WebDriverWait(self.driver, 50).until(
                EC.presence_of_element_located((By.ID, "account-avatar-container"))
            )
            self.driver.quit()
            return True
        except (TimeoutException, NoSuchElementException):
            self.driver.quit()
            return False

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
        allUserInfo = self.getAllUserInfo()
        # 并且为这所有的用户构建一个全局字典
        self.allUserInfoDict = {}
        for user in allUserInfo:
            self.allUserInfoDict[user] = False
        print(allUserInfo)
        # 另外，能在SAVEUSER里面的都是已经登录过的qq
        threads = []  # 定义一个线程池
        for user in allUserInfo:
            threads.append(threading.Thread(
                target=self._singleSubmit, args=(user, url, mydict[user])))

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

    def _singleSubmit(self, userinfo: str, url: str, mydict: dict):
        """构建单个用户options

        Args:
            userinfo (str): 用户qq号
            url (str): 访问的url
            mydict (dict): 提交的用户信息
        """
        # 构建对应的UserData位置
        # chromeUserData = "user-data-dir="+os.getcwd()+"\\"+SAVEUSERFOLDER + \
        #     "\\"+userinfo

        chromeUserData = "user-data-dir=" + SAVEUSERFOLDER + "\\" + userinfo


        # 为单个用户生成一个chrome的options
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("window-size=1920x1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36")
        options.add_argument(chromeUserData)
        prefs = {"profile.managed_default_content_settings.images": 0}  # 加载图片
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        try:
            driver.find_element(By.CLASS_NAME, "user-info-wrap")
        except NoSuchElementException:
            print("该账号未登录")
            driver.quit()
            return False
        else:
            # 登录的情况下，执行
            # 填写表单
            try:
                time.sleep(2)
                elements = driver.find_elements(
                    By.XPATH, "//span[@class='form-auto-ellipsis']")
                for index in range(len(elements)):
                    element = driver.find_elements(
                        By.XPATH, "//span[@class='form-auto-ellipsis']")[index]
                    span_text = element.text
                    node = driver.find_elements(By.TAG_NAME, 'textarea')[index]

                    # 修改div[class = form-simple-main form-ui-component-basic size-small multiple with-border]
                    parent_div = node.find_element(By.XPATH, '../..')
                    driver.execute_script(
                        "arguments[0].classList.add('focus');", parent_div)
                    if mydict.get(span_text) is not None:
                        node.send_keys(mydict[span_text])
                    else:
                        node.send_keys(" ")
                    driver.execute_script(
                        "arguments[0].classList.remove('focus');", parent_div)
                time.sleep(0.2)
                driver.execute_script("arguments[0].click();", driver.find_element(
                    By.XPATH, '//button[text()="提交"]'))
                time.sleep(0.2)
                driver.execute_script("arguments[0].click();", driver.find_element(
                    By.XPATH, '//div[text()="确认"]'))
                self._sleep(1)  # 等待1s
                driver.quit()
                self.allUserInfoDict[userinfo] = True
                return True
            except Exception as E:
                traceback.print_exc()
                return False


# txwd_url = r"https://docs.qq.com/desktop"  # 测试时候用的
# s = SubmitClass()
# mydict = {"userid":
#           {'你的姓名': "xxx", '你的学号': '22222222',
#            '是否确保能按时参加会议': '是', '你的班级': '222222'},
#           "2547496916":
#           {'你的姓名': "张子康", '你的学号': '2022710475', '是否确保能按时参加会议': '是',
#                    '你的班级': '测绘QX221'},
#           "3096828464":
#           {'你的姓名': "张子康2", '你的学号': '2022710475', '是否确保能按时参加会议': '是',
#                    '你的班级': '测绘QX221'},
#           }
# s.submit(txwd_url, mydict)
# s.login('2547496916', txwd_url)
# # s.login('3096828464', txwd_url)
# time.sleep(5)
