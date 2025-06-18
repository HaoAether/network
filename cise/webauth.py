import argparse
import subprocess
import os
import datetime
import netifaces
import requests
import functools
import sys
from model import RequestParams
from auth import mobile_agent, pc_agent, rq_url


#记录方法调用
def log_method_calls(log_func_getter):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            instance = args[0]
            log_func = log_func_getter(instance)
            method_name = func.__name__
            log_func(f"[Info] Entering method: {method_name}")

            try:
                result = func(*args, **kwargs)
                log_func(f"[Info] Exiting method: {method_name}")
                return result
            except Exception as e:
                log_func(f"[Error] Error in method {method_name}: {e}")
                raise
        return wrapper
    return decorator

#检查网络连通性
def check_connectivity_before_auth(log_func_getter, connect_test_func_getter):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            instance = args[0]
            connect_test_func = connect_test_func_getter(instance)
            log_func = log_func_getter(instance)

            if connect_test_func():
                log_func("[Info] Nic is already connected to the internet, skipping authentication.")
                sys.exit(0)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# 认证工具
class BaseAuthenticator:
    #初始化
    def __init__(self):
        self.log_file = ""
        self.log_size_max = 102400
    #打印帮助信息
    def print_help(self):
        print("Help Prompt - Base Authenticator Script")
        print("    Option Format - <key=value>")
    #检查日志文件大小，如果超过最大值则删除
    def check_log_size(self):
        log_dir = "/var/log/cise"
        log_path = os.path.join(log_dir, self.log_file)
        if os.path.exists(log_path):
            log_file_size = os.path.getsize(log_path)
            if log_file_size >= self.log_size_max:
                os.remove(log_path)
        
    #记录日志信息
    def echo_log(self, content):
        date_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        log_dir = "/var/log/cise"
        log_path = os.path.join(log_dir, self.log_file)

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        if not os.path.exists(log_path):
            with open(log_path, 'w') as f:
                pass

        self.check_log_size()

        with open(log_path, 'a') as f:
            f.write(f"[{date_time}] {content}\n")

# 发送request请求
class CiseAuthRequest:
    def __init__(self, timeout_second, logger_callback):
        self.timeout_second = timeout_second
        self.echo_log = logger_callback 

    @log_method_calls(lambda instance: instance.echo_log)
    def send_auth_request(self, url, content, user_agent):
        try:
            headers = {'User-Agent': user_agent, 'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post(
                url,
                data=content,
                headers=headers,
                timeout=self.timeout_second,
                verify=False,
            )
            status_code = response.status_code
            self.echo_log(f"[Info] HTTP CODE {status_code}")
            return True 
        except requests.exceptions.RequestException as e:
            self.echo_log(f"[Error] Auth Request Failed: {e}")
            return False
        except Exception as e:
            self.echo_log(f"[Error] An unexpected error occurred during the request: {e}")
            return False

# 认证工具
class CiseAuth(BaseAuthenticator):
    
    def __init__(self):
        super().__init__()
        self.connect_test_addr = "223.5.5.5"
        self.timeout_second = 5
        self.ping_times = 8
        self.device = "2"  # 默认移动端

        self.username = ""
        self.password = ""
        self.nic = ""
        self.user_agent = ""
        self.ip = ""
        self.mac = ""

        self.request_handler = CiseAuthRequest(
            timeout_second=self.timeout_second,
            logger_callback=self.echo_log 
        )

    def print_help(self):
        """打印 CiseAuth 特定的帮助信息"""
        super().print_help()
        print("        <nic> - Network Interface Card Name")
        print("        <username> - WebAuth Account 'School ID'")
        print("        <password> - WebAuth Password 'School ID' password'")

    @log_method_calls(lambda instance: instance.echo_log)
    #执行网络连通性测试
    def connect_test(self):
        try:
            result = subprocess.run(
                ['ping', '-I', self.nic, self.connect_test_addr, '-q', '-c', str(self.ping_times)],
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except FileNotFoundError:
            self.echo_log("[Error] 'ping' command not found. Please ensure ping is installed.")
            return False
        except Exception as e:
            self.echo_log(f"[Error] Ping test failed: {e}")
            return False

    def option_parse(self, args):
        
        if len(args) < 3:
            self.print_help()
            sys.exit(0)

        for arg in args:
            if '=' in arg:
                option, value = arg.split('=', 1)
                if not value:
                    self.print_help()
                    sys.exit(1)

                if option == "username":
                    self.username = value
                elif option == "password":
                    self.password = value
                elif option == "nic":
                    self.nic = value
                else:
                    self.print_help()
                    sys.exit(1)
            else:
                self.print_help()
                sys.exit(1)

    @log_method_calls(lambda instance: instance.echo_log)
    #获取指定网卡的MAC地址和IP地址
    def get_network_info(self):
        try:
            if self.nic not in netifaces.interfaces():
                self.echo_log(f"[Error] {self.nic} does not exist")
                return False

            self.mac = netifaces.ifaddresses(self.nic)[netifaces.AF_LINK][0]['addr']

            if netifaces.AF_INET in netifaces.ifaddresses(self.nic):
                self.ip = netifaces.ifaddresses(self.nic)[netifaces.AF_INET][0]['addr']
            else:
                self.echo_log("[Error] IP is null, interface might not be up or have an IP address.")
                return False

            self.echo_log(f"[Info] Obtained IP: {self.ip}, MAC: {self.mac}")
            return True
        except Exception as e:
            self.echo_log(f"[Error] Failed to get network info for {self.nic}: {e}")
            return False

    @check_connectivity_before_auth(
        log_func_getter=lambda instance: instance.echo_log,
        connect_test_func_getter=lambda instance: instance.connect_test
    )
    @log_method_calls(lambda instance: instance.echo_log)
    def perform_authentication(self):
        """执行实际的网络认证过程。"""
        url = rq_url.replace('${ip}', self.ip).replace('${mac}', self.mac)
        self.echo_log(f"[Info] URL that has already been built: {url}")

        rp_generator = RequestParams(username=self.username, password=self.password)
        content = ""
        if self.device == "1":  # PC端
            self.user_agent = pc_agent
            content = rp_generator.get_pc()
        elif self.device == "2":  # 移动端
            self.user_agent = mobile_agent
            content = rp_generator.get_mobile()
        else:
            self.echo_log("[Error] The device type is error")
            sys.exit(1)

        self.echo_log(f"[Info] Body that has already been built: {content}")

        request_sent_successfully = self.request_handler.send_auth_request(url, content, self.user_agent)

        # 即使请求发送成功，也需要再次测试网络是否认证成功
        if self.connect_test():
            self.echo_log(f"[Info] Online IP: {self.ip} MAC: {self.mac}")
        else:
            self.echo_log("[Error] UnOnlie") 

    #主函数
    def main(self):
        self.option_parse(sys.argv[1:])

        self.log_file = f"{self.nic}.log"
        self.echo_log(f"[Info] <{self.nic}> Starting Auth")

        if not self.get_network_info():
            sys.exit(1)

        self.perform_authentication()

if __name__ == "__main__":
    auth = CiseAuth()
    auth.main()