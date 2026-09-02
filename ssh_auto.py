import pexpect
import time
import sys
import threading
import os

HOST = os.getenv("HOST")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
SECRET = os.getenv("SECRET")
KEEP_TIME = int(os.getenv("KEEP_TIME", "30"))


def read_output(child):
    """实时读取 SSH 输出（适用于无终端环境）"""
    try:
        data = child.read_nonblocking(size=1024, timeout=0.1)
        sys.stdout.write(data.decode("utf-8", errors="ignore"))
        sys.stdout.flush()
    except:
        pass


def auto_exit(child):
    """限时自动退出"""
    time.sleep(KEEP_TIME)
    print(f"\n>>> 已达到限时 {KEEP_TIME} 秒，自动退出 SSH\n")
    try:
        child.sendline("exit")
    except:
        pass


def main():
    ssh_command = f'ssh -o "StrictHostKeyChecking=no" -o "SetEnv SECRET={SECRET}" {USER}@{HOST}'
    print(f"启动SSH：{ssh_command}")

    child = pexpect.spawn(ssh_command, timeout=30)

    while True:
        idx = child.expect(
            [
                "password:",
                "Permission denied",
                pexpect.EOF,
                pexpect.TIMEOUT,
            ]
        )

        if idx == 0:
            print("\n>>> 检测到密码提示，发送密码\n")
            child.sendline(PASSWORD)
            break

        elif idx == 1:
            print("密码错误或被拒绝")
            return

        elif idx == 2:
            print("连接被关闭")
            return

        elif idx == 3:
            print("等待提示超时")
            continue

    # 启动限时退出线程
    threading.Thread(target=auto_exit, args=(child,), daemon=True).start()

    print("\n>>> 已登录，开始实时输出 SSH 内容\n")

    # 主循环：实时输出 SSH 内容
    while True:
        read_output(child)
        if not child.isalive():
            break

    print("\n>>> SSH 会话已结束\n")


if __name__ == "__main__":
    main()
