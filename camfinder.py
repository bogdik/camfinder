# -*- coding: utf-8 -*-
from lxml import etree
import cv2,base64,threading,time
from queue import Queue

def prepareUrl(url):
    if not '/' == url[0]:
        url='/'+url
    url=url.replace('[CHANNEL]', str(channel)).replace('[USERNAME]', login).replace('[PASSWORD]', password).replace("[WIDTH]", "320").replace("[HEIGHT]", "240")
    if '[AUTH]' in url:
        print()
        url= url.replace('[AUTH]', str(base64.b64encode(bytes('%s:%s'%(login,password),'ascii')))[2:-1])
    return url

class OpenLinker(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
    def run(self):

        while True:
            url = self.queue.get()
            self.opener(url)
            self.queue.task_done()
    def opener(self,url):
        cap = cv2.VideoCapture(url)
        ret, frame = cap.read()
        while ret:
            print("Camera link found: %s" % (url))
            ret, frame = cap.read()
            cv2.imshow("frame", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
        cap.release()

def parseXML(xmlFile):
    with open(xmlFile) as fobj:
        xml = fobj.read()
    root = etree.fromstring(bytes(xml, encoding='utf-8'))
    urls={}
    for appt in root.getchildren():
        for elem in appt.getchildren():
            if 'prefix' in elem.attrib and 'url' in elem.attrib:
                if elem.get('url'):
                    if not elem.get('url') in urls.keys() or 'port' in elem.attrib:
                        if not elem.get('url') in urls.keys():
                            urls[elem.get('url')]={'prefix':elem.get('prefix'),'Source':elem.get('Source')}
                        if 'port' in elem.attrib:
                            if not 'port' in urls[elem.get('url')].keys():
                                urls[elem.get('url')]['port']=[elem.get('port')]
                            else:
                                if not elem.get('port') in urls[elem.get('url')]['port']:
                                    urls[elem.get('url')]['port'].append(elem.get('port'))
    queue = Queue()
    for i in range(theads):
        t = OpenLinker(queue)
        t.setDaemon(True)
        t.start()
    i=0
    for key, value in urls.items():
        url=prepareUrl(key)
        if login or password:
            auth="%s:%s@"%(login, password)
        else:
            auth=""
        if 'port' in value.keys():
            for pt in value['port']:
                link="%s%s%s:%s%s" % (value['prefix'],auth, ip,pt, url)
                print("Try %s" % (link))
                while queue.qsize()>=theads:
                    time.sleep(0.01)
                queue.put(link)
            link = "%s%s%s%s" % (value['prefix'],auth, ip, url)
            print("Try %s" % (link))
            while queue.qsize()>=theads:
                time.sleep(0.01)
            queue.put(link)

        else:
            link = "%s%s%s%s" % (value['prefix'],auth, ip, url)
            print("Try %s" % (link))
            while queue.qsize()>=theads:
                time.sleep(0.01)
            queue.put(link)
        time.sleep(0.1)
        i+=1
        print("%s from %s" %(i,len(urls)))
    queue.join()


if __name__ == "__main__":
    theads=4
    ip='10.60.1.100'
    login='admin'
    password=''
    channel=0
    parseXML("Sources.xml")