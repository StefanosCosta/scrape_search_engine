import requests
import urllib.request
from IPython.display import HTML
import re
from bs4 import BeautifulSoup
import time

class scraper():
    def __init__(self):
        self.name = "scraper"
        self.siteUrl = "http://example.python-scraping.com/"
        self.indexArr = []
        self.urlAmount = 0
        # self.docIndex = []

    def getSiteMap(self,url):
        r = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(r,"lxml")
        soup.prettify()
        queue = []

        #get all location tags
        for link in soup.find_all('loc'):
            queue.append(link.text)
        return queue

    def storeDocument(self,text,id,url):
        filename = str(id) + ".txt"
        file = open(filename,'a')
        file.write(url)
        file.write(text)
        file.flush()
        file.close()

    #crawl the site
    def crawl(self,queue,siteUrl):
        id = 0
        accessedQueue = []
        accessedQueue2 = []
        processingQueue = queue
        badurl = siteUrl + "trap"
        #while queue is not finished
        while len(processingQueue) != 0:
            #get curent url
            url = processingQueue[0]

            #send request to url
            print("Queue Length:" + str(len(processingQueue)) )

            #if the unresolved url has not been accessed:
            if not url in accessedQueue2:
                print("sending request to:")
                print(url)
                gh = urllib.request.urlopen(processingQueue[0])
                w = gh.read()
                #get final redirect (resolved) url:
                newlink = gh.geturl()

                #if the url is not the trap:
                if url != badurl and newlink != badurl:

                    if not (newlink in accessedQueue2):
                        id+=1
                        #get its contents:
                        website = BeautifulSoup(w,"lxml")

                        text = ""
                        for title in website.find_all('h1'):
                            print(title.text)
                            text += title.text

                        for table in website.find_all('tr'):
                            print(table.text)

                            add = table.text
                            #if text has a comma
                            if (',' in add):

                                h = add.split()
                                for k in h:
                                    if ("," in k):
                                        commaArray = k.split(',')
                                        # print(commaArray)
                                        counter = 0
                                        for l in commaArray:
                                            if l.isdigit():
                                                counter+=1
                                        if counter == len(commaArray):
                                            #if text is numeric. remove commas
                                            h[h.index(k)] = h[h.index(k)].replace(',','')
                                        else:
                                            #otherwise text is string, replace with space
                                            h[h.index(k)] = h[h.index(k)].replace(',',' ')
                                s = " "
                                text+= s.join(h) + "\n"

                            else:
                                text +=  str(table.text) + "\n"

                        self.storeDocument(text,id,newlink)
                        # accessedQueue.append([id,newlink,1])
                        accessedQueue.append([id,newlink])
                        if newlink == url:
                            accessedQueue2.append(newlink)
                        else:
                            accessedQueue2.append(newlink)
                            accessedQueue2.append(url)


                        for link in website.find_all('a'):
                            if "http" not in link:
                                newlink = siteUrl + str(link.get('href')[1:])

                                if newlink not in accessedQueue2:
                                    processingQueue.append(newlink)

                            else:
                                newlink = str(link.get('href'))

                                if newlink not in accessedQueue2:
                                    processingQueue.append(newlink)
                    else:
                        accessedQueue2.append(url)

                time.sleep(5)

            processingQueue.remove(url)

        # self.docIndex = accessedQueue
        return id

    #build the index
    def index(self,nOfPages):
        indexArray = []

        for i in range(1,nOfPages+1):
            print(i)
            filename = str(i) + ".txt"
            with open(filename,"r") as file:
                print("entering loop")
                wordList = [word for line in file for word in line.split()]
            listSet = list(set(wordList))
            link =wordList[0]
            for word in listSet:

                if not (wordList.index(word) == 0):
                    count = wordList.count(word)
                    indexArray.append( [word,i,count,link])

        previousWord = []
        indexArray.sort()
        print("creating index file")
        with open("index.txt","w") as f:
            for tuple in indexArray:
                if tuple != indexArray[0]:
                    currentword = tuple[0]
                    if currentword == previousWord:
                        f.write(" " + str(tuple[1]) + "#"+ str(tuple[2]) + "#" + str(tuple[3])  )
                    else:
                        f.write("\n" + str(tuple[0]) + " " + str(tuple[1]) + "#"+ str(tuple[2]) + "#"+ str(tuple[3]))
                else:
                    print("HERE")
                    f.write(str(tuple[0]) + " " + str(tuple[1]) + "#"+ str(tuple[2]) + "#"+ str(tuple[3]))
                previousWord = tuple[0]







    #start crawling and build the index
    def build(self):
        # siteUrl = "http://example.python-scraping.com/"
        # queue = ["http://example.python-scraping.com/"]
        queue = self.getSiteMap("http://example.python-scraping.com/sitemap.xml")
        time.sleep(5)
        self.urlAmount = self.crawl(queue,self.siteUrl)
        self.index(self.urlAmount)

    #loads index into self.indexArr
    def load(self):
        indexArray = []
        with open("index.txt","r") as f:
            for line in f:
                arr =  line.split()

                if arr[0][-1] == ':':
                    arr[0] = str(arr[0]).replace(":",'')
                if arr[0][-1] == ')':
                    arr[0] = str(arr[0]).replace(")",'')
                    arr[0] = str(arr[0]).replace("(",'')
                word = arr[0]
                count =0

                for doc in arr[1:]:
                    lineArray = doc.split("#")
                    indexArray.append( [word,int(lineArray[0]),int(lineArray[1]),str(lineArray[2]) ] )

        return indexArray

    #retrieved invertedList for word passed to it
    def getInvertedList(self,word,indexArr):
        invList = []
        for invertedlist in indexArr:
            if word == invertedlist[0]:
                # print(invertedlist)
                invList.append(invertedlist)
        return invList


    #term at atime algorithm for finding results in index:
    def find(self,query,index,NofDocumentsToRetrieve):
    
        L = []
        q = query
        print("PRINTING")
        for w in q:
            listItem = self.getInvertedList(w,self.indexArr)
            L.append(listItem)
        # print(L)
        if not any(L):
            print("Search yielded no results.")
        else:
            for li in L:
                for doc in li:
                    if L.index(li) == 0 and li.index(doc) == 0:
                        A = {doc[1]:{'score':0, 'QueryNum':0, 'link': doc[3] }}
                    else:
                        A[doc[1]] = {'score':0, 'QueryNum':0, 'link': doc[3] }

            for li in L:
                for doc in li:
                    d = doc[1]
                    docnum = doc[2]
                    # location = doc[3]
                    score = A[d]['score']
                    A[d]['score'] = score + docnum
                    A[d]['QueryNum'] += 1

            data = list(A.items())
            # data = set(data)


            data = sorted(data,key = lambda tup :(tup[1]['QueryNum'],tup[1]['score'] ) )
            for result in range(0,NofDocumentsToRetrieve+1):
                if len(data) > result:
                    res = data[len(data)-1-result]
                    print(res[1]['link'] + " Doc Number: " + str(res[0]) + " Score: " + str(res[1]['score']) + " QNum " + str(res[1]['QueryNum']) )

    #prints index list for a certain word
    def indexPrint(self,text):
        invList = []
        for invertedlist in self.indexArr:
            # print(invertedlist)
            if text == invertedlist[0]:
                # print(invertedlist)
                if len(invList) == 0:
                    invList.append(invertedlist[0])
                    invList.append(invertedlist[1:])
                else:
                    invList.append(invertedlist[1:])
        print(invList)


    def displayWelcome(self):
        print("\n\t\tWelcome to Stefanos' Web Scraper. Please enter your commands")
        print("-------------------------------------------------------------------------------------")
        print("--) build                                                                           -")
        print("--) load                                                                            -")
        print("--) print                                                                           -")
        print("--) find                                                                            -")
        print("----exit (to stop client)                                                           -")
        print("----show (to display available commands)                                            -")
        print("-------------------------------------------------------------------------------------")

    def run(self):
            self.displayWelcome()
            while(True):

                command=input().strip().split()

                if not command:                                         # empty
                    continue
                if(command[0]== "build" and len(command)==1):
                    self.build()
                elif(command[0]=="load" and len(command )==1):          # load
                    self.indexArr = self.load()
                    print("done")
                elif(command[0]=="print" and len(command)==2):         # print
                    print(command[1])

                    self.indexPrint(command[1])
                elif(command[0] == "find" and len(command) > 1):       # post
                    self.find(command[1:],self.indexArr,10)
                elif(command[0] == "exit"):                               # exit
                    break
                elif(command[0]=="show" and len(command)==1):             # show
                    self.displayWelcome()

if __name__ == "__main__":
    c = scraper()
    c.run()
