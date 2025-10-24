import os# 操作系统交互
import paramiko# 用于SSH协议实现(1.安全的远程命令执行,2.SFTP文件传输,3.端口转发,4.SSH服务器创建)
# 2.的解释:SFTP = SSH File Transfer Protocol（安全文件传输协议）,
#                就像通过加密的快递服务在两地之间安全地传送文件。
#                普通FTP = 明信片（内容谁都能看）
#                SFTP = 带锁的保险箱（只有收件人有钥匙）
import socket# 用于创建网络连接，实现不同计算机之间的数据交换。
import sys# 用于与Python解释器交互和系统操作
import threading# 用于创建和管理线程，实现并发执行

CWD = os.path.dirname(os.path.realpath(__file__))# 用全大写命名变量 - 常量
# 1.__file__ - 可能返回脚本的相对路径,绝对路径或包含符号链接的路径
# 符号链接(文件):
# 例:一个文件main.py,它的绝对路径是"/mnt/network_drive/documents/main.py"
#    我写一个文件,命名为"/home/user/docs",它的内容是"/mnt/network_drive/documents"
#    main.py的路径就也可以写为"/home/user/docs/main.py"
#    这个文件"/home/user/docs"就是一个符号链接(文件)
# 2.os.path.realpath() - 解析符号链接（如果路径包含符号链接）,转换为绝对路径（如果输入是相对路径）
# 3.os.path.dirname() - 提取路径中的目录部分
# 例:directory = os.path.dirname("/home/user/project/script.py")
#    print(directory)
#    输出:"/home/user/project"
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD,'test_rsa.key'))# 将filename文件中的密钥数据放到HOSTKEY中
# 1.os.path.join(CWD, 'test_rsa.key') - 构建密钥文件完整路径(!!!只是拼接字符串,不会创建任何文件)
# 例: CWD = "/home/user/docs"
#     file_path = os.path.join(CWD, 'test_rsa.key')
#     print(file_path)
#     输出:"/home/user/project/test_rsa.key"
# 2.paramiko.RSAKey()  - 从文件加载RSA密钥

class Server(paramiko.ServerInterface):# Server类继承自paramiko.ServerrInterface类
    # paramiko.ServerrInterface类是包含了SSH服务器基本功能的接口类,Server继承了它自动成为一个合格的SSH服务器
    # 接口类:只定义方法签名而不实现具体功能，让子类去实现这些方法
    def __init__(self):
        self.event = threading.Event()# 创建了一个线程同步事件对象,用于线程间的协调和通信
        #event.set()使线程继续;event.clear()重置事件状态;event.wait()使线程阻塞直到事件被设置;event.is_set()检查当前是继续还是重置

    def check_channl_request(self,kind,chaind):
        if kind == 'session':# session会话
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINSTRATIVELY_PROHIBITED# 因管理原因打开失败

    def check_auth_password(self,username, password):###############需要根据自己机器改动
        if (username == 'kali') and (password == 'kali'):
            return paramiko.AUTH_SUCCESSFUL# 认证成功

if __name__ == '__main__':
    server = '192.168.102.134'###############需要根据自己机器改动
    ssh_port = 2222###############需要根据自己机器改动
    try:
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)# socket.socket() - 返回一个socket对象，用于网络通信
        sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)# setsockopt() - 用于配置socket的各种行为参数
        sock.bind((server,ssh_port))# bind() - 将socket关联到特定的网络地址和端口;服务端必须调用，客户端通常不需要
        sock.listen(100)
        # listen() - 设置为服务端模式,启动TCP连接请求的监听机制
        # 100 - 等待连接队列的最大长度,不是同时服务的客户端数量限制
        print('[+] Listening for connection ...')
        client,addr = sock.accept()# client:新的socket对象;addr:元组(客户端IP,客户端端口)
    except Exception as e:
        print('[-] Listen failed:' + str(e))
        sys.exit(1)# 退出程序并返回状态码1
    else:# 无异常时执行
        print('[+] Got a connection!',client,addr)

    bhSession = paramiko.Transport(client)# paramiko.Transport() - Paramiko 的 SSH 传输层类
    bhSession.add_server_key(HOSTKEY)# 用于注册服务器的主机密钥
    server = Server()
    bhSession.start_server(server=server)# 启动SSH服务器端会话

    chan = bhSession.accept(20)
    # accept() - 用于接受客户端的SSH通道请求;返回Channel对象,用于与客户端通信
    # 20 - 超时时间,若为0或None则无限等待
    if chan is None:
        print('*** No channel.')
        sys.exit(1)

    print('[+] Authenticated!')# 认证成功!
    print(chan.recv(1024))
    chan.send('Welcome to bh_ssh')
    try:
        while True:
            command = input("Enter command:")
            if command != 'exit':
                chan.send(command)
                r = chan.recv(8192)
                print(r.decode())
            else:
                chan.send('exit')
                print('exiting')
                bhSession.close()
                break
    except KeyboardInterrupt:
        bhSession.close()






