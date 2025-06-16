import os
import sys
import subprocess
import datetime
import re
import shutil

# ===== declare variable =====
# 连通性测试IP，若默认的地址不再提供ICMP访问，请切换其它地址
CONNECT_TEST_ADDR = "223.5.5.5"
# curl 命令超时时间
# 单位为秒
TIMEOUT_SECOND = 5
# ping 命令次数
PING_TIMES = 8
# 日志最大大小
LOG_SIZE_MAX = 102400
# 认证设备
# 移动端填2
# PC端填1
# 建议在路由器上只使用移动端
# PC端需要在教室上课时使用
DEVICE = "2"

# 请不要修改以下变量，变量会在后面赋值
username = ""
password = ""
nic = ""
log_file = ""
user_agent = ""

# 日志目录，设置为脚本所在目录下的 logs/cise
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "cise")

# ===== function =====
def print_help():
    """打印帮助信息"""
    # --- 添加调试信息 ---
    print("[DEBUG] print_help called.")
    # --- 调试信息结束 ---
    print("Help Prompt - Cdivtc WebAuth Script")
    print("    Option Format - <key=value>")
    print("        <nic> - Network Interface Card Name")
    print("        <username> - WebAuth Account 'School ID'")
    print("        <password> - WebAuth Password 'School ID' password'")

def check_log_size():
    """检查日志文件大小，如果超过最大值则删除"""
    # --- 添加调试信息 ---
    # print(f"[DEBUG] check_log_size called. Log file: {os.path.join(LOG_DIR, log_file)}") # 这行可能会在文件不存在时报错
    # --- 调试信息结束 ---
    log_path = os.path.join(LOG_DIR, log_file)
    if os.path.exists(log_path):
        log_file_size = os.path.getsize(log_path)
        if log_file_size >= LOG_SIZE_MAX:
            os.remove(log_path)

def echo_log(content):
    """记录日志"""
    date_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    log_path = os.path.join(LOG_DIR, log_file)

    # --- 添加调试信息 ---
    print(f"[DEBUG] echo_log called with content: {content}")
    print(f"[DEBUG] Attempting to create log directory: {LOG_DIR}")
    # --- 调试信息结束 ---

    if not os.path.exists(LOG_DIR):
        try:
            os.makedirs(LOG_DIR)
            print(f"[DEBUG] Log directory created: {LOG_DIR}") # 确认创建成功
        except OSError as e:
            print(f"Error: Could not create log directory {LOG_DIR}. Permission denied or path issue. {e}")
            sys.exit(1)

    if not os.path.exists(log_path):
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                pass # just create the file
            print(f"[DEBUG] Log file created: {log_path}") # 确认文件创建成功
        except IOError as e:
            print(f"Error: Could not create log file {log_path}. Permission denied or path issue. {e}")
            sys.exit(1)


    check_log_size()
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"[{date_time}] {content}\n")
    print(f"[DEBUG] Log content written to file: {log_path}") # 确认内容写入
    # --- 调试信息结束 ---


def connect_test(interface):
    """
    连通性测试
    返回 True 或 False
    """
    # --- 添加调试信息 ---
    print(f"[DEBUG] connect_test called for interface: {interface}")
    # --- 调试信息结束 ---
    try:
        if sys.platform == "win32":
            command = ["ping", CONNECT_TEST_ADDR, "-n", str(PING_TIMES)]
        else:
            command = ["ping", "-I", interface, CONNECT_TEST_ADDR, "-q", "-c", str(PING_TIMES)]

        # --- 添加调试信息 ---
        print(f"[DEBUG] Running ping command: {' '.join(command)}")
        # --- 调试信息结束 ---

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # --- 添加调试信息 ---
        print(f"[DEBUG] Ping command return code: {result.returncode}")
        print(f"[DEBUG] Ping stdout: {result.stdout.decode('gbk', errors='ignore').strip()}")
        print(f"[DEBUG] Ping stderr: {result.stderr.decode('gbk', errors='ignore').strip()}")
        # --- 调试信息结束 ---
        return result.returncode == 0
    except Exception as e:
        print(f"[DEBUG] Exception in connect_test: {e}") # 异常时也打印
        echo_log(f"[Error] Ping failed: {e}") # 仍然写入日志
        return False

def option_parse(args):
    """
    解析命令行参数
    """
    global username, password, nic
    # --- 添加调试信息 ---
    print(f"[DEBUG] option_parse called with arguments: {args}")
    # --- 调试信息结束 ---
    if len(args) < 3:
        print_help()
        sys.exit(0)

    for arg in args:
        # --- 添加调试信息 ---
        print(f"[DEBUG] Parsing arg: {arg}")
        # --- 调试信息结束 ---
        if '=' not in arg:
            print_help()
            sys.exit(1)

        parts = arg.split('=', 1)
        option = parts[0]
        value = parts[1]

        if not value:
            print_help()
            sys.exit(1)

        if option == "username":
            username = value
        elif option == "password":
            password = value
        elif option == "nic":
            nic = value
        else:
            print_help()
            sys.exit(1)
    # --- 添加调试信息 ---
    print(f"[DEBUG] Parsed username: {username}, password: {'*' * len(password)}, nic: {nic}")
    # --- 调试信息结束 ---

# ===== 主程序逻辑 =====
if __name__ == "__main__":
    # --- 添加调试信息 ---
    print("[DEBUG] Script starting...")
    print(f"[DEBUG] sys.argv: {sys.argv}")
    # --- 调试信息结束 ---

    # 参数识别
    option_parse(sys.argv[1:])

    # 日志的划分通过接口名
    log_file = f"{nic}.log"
    echo_log(f"[Info] <{nic}> Starting Auth")

    # 获取IP和MAC
    ip = ""
    mac = ""
    try:
        # --- 添加调试信息 ---
        print(f"[DEBUG] Getting IP and MAC for platform: {sys.platform}")
        # --- 调试信息结束 ---

        if sys.platform == "win32":
            ipconfig_output = subprocess.check_output(
                ["ipconfig", "/all"],
                text=True,
                encoding='gbk',
                errors='ignore'
            )
            # --- 添加调试信息 ---
            # print(f"[DEBUG] ipconfig /all output:\n{ipconfig_output[:500]}...") # 打印部分输出避免过长
            # --- 调试信息结束 ---

            adapter_pattern = re.compile(rf'适配器\s*{re.escape(nic)}[\s\S]*?(?:适配器|$)', re.IGNORECASE)
            adapter_info_match = adapter_pattern.search(ipconfig_output)

            if adapter_info_match:
                adapter_info = adapter_info_match.group(0)
                # --- 添加调试信息 ---
                print(f"[DEBUG] Found adapter info for '{nic}':\n{adapter_info[:200]}...")
                # --- 调试信息结束 ---

                ip_match = re.search(r'IPv4 地址[.\s]*: (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', adapter_info)
                ip = ip_match.group(1) if ip_match else ""

                mac_match = re.search(r'物理地址[.\s]*: ([0-9a-fA-F:-]{17})', adapter_info)
                mac = mac_match.group(1).replace('-', ':').lower() if mac_match else ""
            else:
                echo_log(f"[Error] Could not find adapter '{nic}' in ipconfig output. Please check the NIC name.")
                sys.exit(1)

        else: # Linux/macOS
            subprocess.run(
                ["ip", "link", "show", "dev", nic],
                capture_output=True, text=True, check=True
            )
            link_dev_output = subprocess.check_output(
                ["ip", "address", "show", "dev", nic],
                text=True
            )
            mac_match = re.search(r'link/ether\s+([0-9a-fA-F:]+)', link_dev_output)
            mac = mac_match.group(1).lower() if mac_match else ""
            ip_match = re.search(r'inet\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/\d{1,2}', link_dev_output)
            ip = ip_match.group(1) if ip_match else ""

    except subprocess.CalledProcessError as e:
        print(f"[DEBUG] CalledProcessError in IP/MAC retrieval: {e}") # 打印详细错误
        echo_log(f"[Error] Network interface '{nic}' does not exist or command failed. Details: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[DEBUG] General Exception in IP/MAC retrieval: {e}") # 打印详细错误
        echo_log(f"[Error] Failed to get IP or MAC. Details: {e}")
        sys.exit(1)

    if not ip:
        echo_log("[Error] IP is null, check if the network adapter is active and has an IP address.")
        sys.exit(1)
    if not mac:
        echo_log("[Error] MAC is null, check if the network adapter is active.")
        sys.exit(1)

    # Testing connectivity
    echo_log(f"[Info] Current IP: {ip}, MAC: {mac}")
    if connect_test(nic):
        echo_log("[Info] Nic is already connected to the internet.")
        sys.exit(0)
    else:
        echo_log("[Info] Nic is not connected to the internet, attempting authentication.")

    url = f"http://172.16.4.32/webauth.do?wlanuserip={ip}&wlanacname=bras&wlanusermac={mac}"
    echo_log(f"[Info] URL that has already been built: {url}")

    content = ""
    header = ""
    if DEVICE == "1":
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/555.55 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/555.55" # 稍微修改User-Agent避免重复
        content = f"hostIp=http://127.0.0.1:8083&loginType=&auth_type=0&isBindMac1=0&pageid=1&templatetype=1&listbindmac=0&recordmac=0&isRemind=1&loginTimes=&groupId=&distoken=&echostr=&url=&isautoauth=&notice_pic_loop1=/portal/uploads/pc/demo3/images/logo.jpg&notice_pic_loop2=/portal/uploads/pc/demo3/images/rrs_bg.jpg&userId={username}&passwd={password}"
    elif DEVICE == "2":
        user_agent = "Mozilla/55.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1" # 稍微修改User-Agent避免重复
        content = f"hostIp=http://127.0.0.1:8080&loginType=&auth_type=0&isBindMac1=0&pageid=2&templatetype=2&listbindmac=0&recordmac=0&isRemind=0&loginTimes=&groupId=&distoken=&echostr=&url=&isautoauth=&notice_pic_loop1=/portal/uploads/mobile/demo3/images/logo.jpg&userId={username}&passwd={password}"
    else:
        echo_log("[Error] The device type is error. Please set DEVICE to '1' (PC) or '2' (Mobile).")
        sys.exit(1)

    echo_log(f"[Info] Body that has already been built: {content}")

    try:
        curl_command = [
            "curl",
            "-A", user_agent,
            "-X", "POST",
            "-Ls",
            "-o", "/dev/null",
            "-w", "%{http_code}\n",
            "--max-time", str(TIMEOUT_SECOND),
            "-d", content,
            url
        ]
        # --- 添加调试信息 ---
        print(f"[DEBUG] Running curl command: {' '.join(curl_command)}")
        # --- 调试信息结束 ---

        result = subprocess.run(
            curl_command, 
            capture_output=True, text=True, check=False
        )
        status_code = result.stdout.strip()
        # --- 添加调试信息 ---
        print(f"[DEBUG] Curl stdout: {result.stdout.strip()}")
        print(f"[DEBUG] Curl stderr: {result.stderr.strip()}")
        # --- 调试信息结束 ---
    except FileNotFoundError:
        print("[DEBUG] 'curl' command not found error.") # 直接打印到控制台
        echo_log("[Error] 'curl' command not found. Please ensure curl is installed and accessible in your system's PATH.")
        sys.exit(1)
    except Exception as e:
        print(f"[DEBUG] Exception during curl execution: {e}") # 直接打印到控制台
        echo_log(f"[Error] Curl command failed: {e}")
        status_code = "000"

    echo_log(f"[Info] HTTP CODE {status_code}")

    if connect_test(nic):
        echo_log(f"[Info] Online IP: {ip} MAC: {mac}")
    else:
        echo_log("[Error] UnOnline - Authentication might have failed or network still not connected.")
    # --- 添加调试信息 ---
    print("[DEBUG] Script finished.")
    # --- 调试信息结束 ---