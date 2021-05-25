# python Socket 编程。参考文档：https://docs.python.org/zh-cn/3/howto/sockets.html
import socket
import threading
import datetime
# 创建 socket 接口，并且绑定来自 0.0.0.0（即任意） 的 9906 端口
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(("0.0.0.0", 9906))
serversocket.listen()

# 多线程操作的一个框架。每个实例是一个线程
class client_thread(threading.Thread):
    client_socket = None
    client_address = None
    d: dict = {}
    def __init__(self, clientSocket, addr):
        # 如果新收到一个连接,则创建一个新线程,并且拿到客户端的信息
        # 与该客户端连接的 socket 和 addr
        threading.Thread.__init__(self)
        self.client_socket = clientSocket
        self.client_address = addr

    # 主函数
    def run(self):
        print("Begin of a request", end=": ")
        print("%s:%d" % (self.client_address[0], self.client_address[1]), end="\n")
        while True:
            buffer = b""
            rec = b""
            status = 0
            while True:
                buffer = self.client_socket.recv(1)
                rec += buffer
                # 状态转移的思路
                # 0 普通状态（正常读取），如果读入了一个 \r 那么到 1
                # 1 已经读入一个了 \r，如果再次读到一个 \n 那么到 2
                # 2 此时已经有了一个 \r\n，再读取一次，如果是其他字符说明是普通换行，回到 0
                    # 如果是 \r 那么可能是 \r\n\r\n 分界线，到 4 继续读取
                # 3 再读取一个，如果是 \n 成功读入 \r\n\r\n
                    # 此时对于一个 GET 请求已完成，跳转 4 标记结束
                # 4 结束
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
            # 调用 process 函数，对 rec（HTTP 报文）进行处理
            self.client_socket.send(self.process(rec))
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), end=", ")
            print("%s:%d" % (self.client_address[0], self.client_address[1]), end=", ")
            print(rec, end="\n")
            self.client_socket.close()
            break
        self.client_socket.close()
        # exit(0)
    def process(self, recv):
        # recv 是服务器收到的报文原始数据（字符串），在这里写处理函数
        # 下面是一个例子

        request = self.process_header(recv) # 解析 HTTP 报文，到 python 字典等数据类型
        print(request)
        
        # 利用 python 解析后的东西，进行动态的处理
        # 这里面是两个例子
        # 分别是通过 path 实现的计算器
        # 和 动态时间显示
        path = request["path"][1:]
        path_split = path.split("/")
        if path_split[0] == "setarg1":
            self.d["arg1"] = int(path_split[1])
        if path_split[0] == "setarg2":
            self.d["arg2"] = int(path_split[1])
        if path_split[0] == "setOpe":
            self.d["operation"] = path_split[1]
            print("operation is " + self.d["operation"])
        response = self.response2http(200, f'success')
        if path_split[0] == "getVal":
            val = 0
            if self.d["operation"] == "add":
                val = self.d["arg1"] + self.d["arg2"]
            if self.d["operation"] == "minus":
                val = self.d["arg1"] - self.d["arg2"]
            if self.d["operation"] == "mul":
                val = self.d["arg1"] * self.d["arg2"]
            if self.d["operation"] == "div":
                val = self.d["arg1"] // self.d["arg2"]
            response = self.response2http(200, f'{self.d["arg1"]} {self.d["operation"]} {self.d["arg2"]} = {val}')
        if path_split[0] == "time":
            import datetime
            file = open("time.html", "r", encoding="utf8")
            text = file.read()
            text = text.replace("{{time}}", datetime.datetime.strftime(datetime.datetime.now(), "%D %T"))
            response = self.response2http(200, text)
        return response

    def process_header(self, recv):
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

    def response2http(self, code, data):
        t = f"HTTP/1.1 {code} OK\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n{data}\r\n"
        return t.encode("utf-8")



while True:
    (clientsocket, address) = serversocket.accept()
    ct = client_thread(clientsocket, address)
    ct.start()

