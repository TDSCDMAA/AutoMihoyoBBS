from asyncio import Condition
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import json

class GeetestValidateServer:
    validate = None
    lock = threading.Condition()
    #主线程调用，调用后在新线程开启服务器，等待服务器自己结束
    def solveCaptcha(self,challenge:str,gt:str)->str:
        #用__handlerFactory__创建一个BaseHTTPRequestHandler类，然后创建一个httpServer来处理请求，端口是16384
        ts = HTTPServer(('127.0.0.1', 16384), self.__handlerFactory__({"challenge":challenge,"gt":gt},self,self.lock))
        serverThread = threading.Thread(target=self.__startServer__,args=(ts,))
        #主线程比server线程跑得快，开一个线程用来等待lock
        waitThread = threading.Thread(target=self.__waitForLock__)
        serverThread.start()
        waitThread.start()
        waitThread.join()
        ts.shutdown()
        return self.validate["geetest_validate"]

    #开一个线程用来等待lock
    def __waitForLock__(self):
        self.lock.acquire()
        self.lock.release()

    #网页服务器线程
    def __startServer__(self,server:HTTPServer):
        self.lock.acquire()
        server.serve_forever()


    def __handlerFactory__(self,challenge:dict,validateServer,lock:Condition):
        class HandlerWithChallenge(BaseHTTPRequestHandler):
            challengeInfo = challenge
            server = validateServer
            def responseBuilder(self,responseStr:str):
                # 响应头
                headers = "HTTP/1.1 200 OK\nContent-Length: {data-length}\nContent-Type: text/html; charset=utf-8\n".replace('\n', '\r\n') + '\r\n'
                # 内容的长度要用utf8编码下的算
                utf8Data = responseStr.encode("utf-8")
                headers = headers.format_map({'data-length': len(utf8Data)})
                self.wfile.write(headers.encode())
                self.wfile.write(utf8Data)

            def do_GET(self):
                #发送网页
                if self.path =="/":
                    f = open(file="index.html",mode="r",encoding="utf-8")
                    self.responseBuilder(f.read())
                    f.close()
                #处理一下图标
                elif self.path =="/favicon.ico":
                    self.responseBuilder("")
                else:
                    self.send_error(404,"Not Found")

            def do_POST(self):
                # 获得报文的长度
                responseData = self.rfile.read(int(self.headers['content-length']))
                #获得challenge的信息
                if self.path =="/getChallenge":
                    data = json.dumps(self.challengeInfo)
                    self.responseBuilder(data)
                #前端返回geetest的validate信息，结束服务器运行
                elif self.path =="/complete":
                    validateObj = json.loads(responseData)
                    self.responseBuilder('{"code":1}')
                    #存到GeetestValidateServer的validate中
                    validateServer.validate = validateObj
                    #唤醒主线程，关闭服务器
                    lock.release()
                else:
                    self.send_error(404,"Not Found")
        return HandlerWithChallenge