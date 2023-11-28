import asyncio

def add(a, b):
    return a+b

def unpackingtest(condition):
    res = add(*(condition))
    print(res)

def checkUserLogin(sub, username, url, waitSecond=10):
    '''
        该函数用来开启线程任务
    Args:
        sub (SubmitClass): submitclass对象
        username (string): 检测qq号
        waitSecond (int):  浏览器显示等待时间   

    '''
    pass



async def foo(x):
    print("这是一个协程:", x)
    return "返回值"


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        print("开始运行协程")
        coro = foo(2)
        print("进入事件循环")
        result = loop.run_until_complete(coro)
        print(f"run_until_complete可以获取协程的{result}，默认输出None")
    finally:
        print("关闭事件循环")
        loop.close()
