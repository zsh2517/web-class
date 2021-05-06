# python Socket 编程。参考文档：https://docs.python.org/zh-cn/3/howto/sockets.html
import socket
import threading
import datetime
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(("0.0.0.0", 9901))
serversocket.listen()

class client_thread(threading.Thread):
    client_socket = None
    client_address = None
    def __init__(self, clientSocket, addr):
        threading.Thread.__init__(self)
        self.client_socket = clientSocket
        self.client_address = addr

    def run(self):
        print("Begin of a request", end=": ")
        print("%s:%d" % (self.client_address[0], self.client_address[1]), end="\n")
        while True:
            # time.sleep(3)
            buffer = b""
            rec = b""
            status = 0
            while True:
                buffer = self.client_socket.recv(1)
                rec += buffer
                if buffer == b"\r":
                    if status == 0:
                        status = 1
                    elif status == 2:
                        status = 3
                    else:
                        status = 0
                elif buffer == b"\n":
                    if status == 1:
                        status = 2
                    elif status == 3:
                        status = 4
                        break
                    else:
                        status = 0
                else:
                    status = 0
            self.client_socket.send(self.process(rec))
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), end=", ")
            print("%s:%d" % (self.client_address[0], self.client_address[1]), end=", ")
            print(rec, end="\n")
            self.client_socket.close()
            break
        self.client_socket.close()
        # exit(0)
    def process(self, recv):
        # recv 是服务器收到的数据，在这里写处理函数
        # 下面是例子
        request = self.process_example(recv)
        # data = b""
        # data = open("helloworld", "rb").read()
        response = self.response_example(200, f"Hello {request['path'][1:]}")
        return response

    def process_example(self, recv):
        data = recv.decode("utf-8")
        headers = {}
        t = data.split("\r\n\r\n")
        # 解析 headers
        lines = t[0].split("\r\n")
        for line in lines[1:]:
            x = line.split(":", 1)
            print(x)
            headers[x[0]] = x[1]
        methods = lines[0]
        print(headers)

        # 解析 请求地址
        temp = lines[0]
        method, path, http_version = temp.split(" ", 3)
        if "%" in path:
            newpath = ""
            temppath = bytearray()
            ptr = 0
            while ptr < len(path):
                print(newpath, temppath)
                if path[ptr] != "%":
                    if len(x) != 0:
                        newpath += temppath.decode("utf8")
                        temppath = bytearray()
                    newpath += path[ptr]
                    ptr += 1
                else:
                    temppath.append(int(path[ptr + 1] + path[ptr + 2], 16))
                    ptr += 3
            if len(temppath) != 0:
                newpath += temppath.decode("utf8") 
            path = newpath
        return {
            "method": method,
            "path": path,
            "version": http_version,
            "headers": headers
        }

    def response_example(self, code, data):
        t = f"HTTP/1.1 {code} OK\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n{data}\r\n"
        return t.encode("utf-8")



while True:
    (clientsocket, address) = serversocket.accept()
    ct = client_thread(clientsocket, address)
    ct.start()

