#! /usr/bin/env python
import json
from urllib.parse import quote,urlparse
import requests,sys,re,threading
import queue as Queue
regex = (r"cgiData = (.*?);\n"
	r"    </script>")


class checkThread(threading.Thread):
    def __init__(self, url_queue:Queue.Queue):
        super(checkThread, self).__init__()
        self.url_queue = url_queue

    def run(self):
        while True:
            if not self.url_queue.empty():
                try:
                    url = self.url_queue.get_nowait()
                    res =self.check(url)
                    if res!=True:
                        if '该地址为IP地址' in res['desc']:continue
                        if res['type']=='empty':
                            print(f"{url:s} :{res['title']:s}")
                        else:
                            print(f"{url:s} :{res['desc']:s}")
                except Queue.Empty:
                        break
            else:
                break
    @staticmethod
    def check(url):
        resp=requests.get(f'https://mp.weixinbridge.com/mp/wapredirect?url={quote(url)}',allow_redirects=False)
        if resp.status_code!=302:
            print("情况不对劲，可能接口被风控，暂停！")
            print(f"当前URL：{url}, 可过段时间继续从此位置继续扫描")
            exit()
            return True
        if "weixin110.qq.com" not in resp.headers["Location"]:
            return True
        resp2 = requests.get(resp.headers["Location"])
        matches = re.findall(regex, resp2.text, re.MULTILINE)
        if len(matches)!=0:
            return json.loads(matches[0])
        return True

def main():
    url_queue = Queue.Queue()
    s=set()
    with open(sys.argv[1],"r") as f:
        for l in f:
            l=l.strip()
            if not l.startswith('http'):
                continue
            up=urlparse(l)
            l=up.scheme+'://'+up.netloc
            s.add(l)
        for i in s:
            url_queue.put(i)
    print(f"已提取{len(s)}个域名,开始检测")
    threads = []
    for i in range(1):# 已测试  2线程都会被风控。
        chT= checkThread(url_queue)
        threads.append(chT)
        chT.start()
    for t in threads:
        t.join()
if __name__=="__main__":
    if len(sys.argv)<2:
        print(checkThread.check("https://vshex.com"))

    else:
        main()