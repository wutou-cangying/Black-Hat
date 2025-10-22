#TCP代理是什么？
#TCP代理是一个位于客户端和目标服务器之间的程序，它：

#接收客户端的连接请求

#建立到目标服务器的连接

#在两者之间转发数据

import sys
import socket
import threading

# 十六进制转储过滤器
HEX_FILTER = ''.join(
    [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)])
# chr(i)-将整数转换为对应的字符
# repr(chr(i))-获取该字符的python字符串表示形式
# len(repr(chr(i))) == 3 - 检查长度是否为 3,
# 为什么长度等于3就是可打印字符？可打印字符：repr('A') 返回 'A'（长度为3，包含两边的引号）;不可打印字符：repr('\x00') 返回 '\x00'（长度大于3，包含转义序列）
# A and B or C-A为True返回B;A为False返回C

def hexdump(src, length = 16,show = True):
    if isinstance(src,bytes):# 检查src是否是bytes类型
        src = src.decode()

    results = list()
    for i in range(0, len(src), length):
        word = str(src[i:i+length])# src中截取一段转换成字符串
        printable = word.translate(HEX_FILTER)# translate()把不可打印字符过滤(即去掉)
        hexa = ' '.join([f'{ord(c):02x}' for c in word])
        # ' '.join()用空格连接所有的十六进制字符串
        # ord(c)获取字符的ASCII码
        # 02x:将整数化为2位十六进制字符串,不足的用0补齐
        hexwidth = length*3
        # >>> chr(65)
        # 'A'
        # >>> chr(30)
        # '\xle'
        # >>> len(repr(chr(65)))
        # 3
        # >>> len(repr(char(30)))
        # 6
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
        # hexa:十六进制字符串(如"48 65 6c 6c 6f")
        # :<:左对齐
        # {hexwidth}:动态宽度值(花括号内再次使用变量)
        # 整体作用:将hexa左对齐,总宽度为hexwidth个字符
        if show:
            for line in results:
                print(line)
        else:
            return results

def receive_from(connection):
    buffer = b""
    connection.settimeout(5)# 设置socket操作的超时时间为5秒.如果5秒内没有数据收发,会抛出socket.timeout异常.防止程序无限期等待
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer

# 你可能想在转发数据包之前,修改一下回复的数据包或请求的数据包
def request_handler(buffer):
    # perform packet modification
    return buffer

def response_handler(buffer):
    # perform packet modification
    return buffer

def proxy_handler(client_socket,remote_host,remote_port,receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
        # [<==]-表示从远程发往本地
        # %-字符串格式化,将len(remote_buffer)的结果插入到%d位置
        client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = "[==>]Received %d bytes from localhost." % len(local_buffer)
            print(line)
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break

def server_loop(local_host,local_port,remote_host,remote_port,receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host,local_port))
    except Exception as e:
        print('problem on bind: %r' % e)
        # %r-repr(e)返回对象的官方字符串表示

        print("[!!] Failed to listen on %s:%d" % (local_host,local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)

    print("[*] Listening on %s:%d" % (local_host,local_port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        # print out the local connection information
        line = "> Received incoming connection from %s:%d" % (addr[0],addr[1])
        print(line)
        # start a thread(线程) to talk to the remote host
        proxy_thread = threading.thread(
            target = proxy_handler,
            args = (client_socket,remote_host,
                    remote_port,receive_first))
        proxy_thread.start()

def main():
    if len(sys.argv[1:]) != 5:
        # sys.argv是命令行参数的列表
        # 命令:python netcat.py -t 127.0.0.1 -p 5555 -l -c
        # 对应的sys.argv:sys.argv = [
                                #     'netcat.py',    # argv[0]
                                #     '-t',           # argv[1]
                                #     '127.0.0.1',    # argv[2]
                                #     '-p',           # argv[3]
                                #     '5555',         # argv[4]
                                #     '-l',           # argv[5]
                                #     '-c'            # argv[6]
                                # ]
        # 所以sys.argv[1:] = 除了脚本名外的所有参数
        print("Usage: ./proxy.py [localhost] [localport]",end = '')# usage-使用说明
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host,local_port,remote_host,remote_port,receive_first)

    if __name__ == '__main__':
        main()