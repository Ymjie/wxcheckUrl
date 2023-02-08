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
    with open(sys.argv[1],"r") as f:
        for l in f:
            l=l.strip()
            if not l.startswith('http'):
                continue
            up=urlparse(l)
            l=up.scheme+'://'+up.netloc
            print(l)
            url_queue.put(l)
    threads = []
    for i in range(5):
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