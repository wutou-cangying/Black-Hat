import paramiko

def ssh_command(ip,port,user,passwd,cmd):
    client = paramiko.SSHClient()# 通过SSH连接远程服务器
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 当你第一次SSH连接新服务器时，会看到这样的警告：
    # The authenticity of host 'xxx' can't be established.
    # RSA key fingerprint is xxx.
    # Are you sure you want to continue connecting(yes / no)?
    # client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 就是自动回答 "yes"。
    client.connect(ip,port = port,username = user,password = passwd)

    _,stdout,stderr = client.exec_command(cmd)
    # 变量1,变量2,变量3 = exec_command(要执行的命令)-用于在远程服务器上执行命令
    # stdin:输入流(向命令发送数据)[你告诉服务员要什么菜（输入）]
    # stdout:输出流(获取命令的正常输出)[服务员端来的菜（正常输出）]
    # stderr:错误流(获取命令的错误信息)[服务员说"这个菜卖完了"（错误信息）]
    output = stdout.readlines() + stderr.readlines()
    if output:
        print('--- Output ---')
        for line in output:
            print(line.strip())

if __name__ == '__main__':
    import getpass# 隐藏用户输入的内容，防止被旁人看到。
    # user = getpass.getuser()
    # 使用getpass库来获取当前设备上登录用户的用户名，但因为
    # 服务器和当前设备上的用户名不同，所以这里明确要求用户输入用户名
    user = input('Username:')
    password = getpass.getpass()
    # 让用户输入密码(敲击的字符不会出现在屏幕上)

    ip = input('Enter server IP:') or '192.168.102.134'
    port = input('Enter port or <CR>:') or 2222# 回车键(Enter键)
    cmd = input('Enter command or <CR>:') or 'id'# 一个Linux命令
    ssh_command(ip,port,user,password,cmd)



