#!/bin/bash

# Author: 肖翼
# Blog: https://www.xoneki.cn
# Date: 2024年9月6日
# LastUpdate: 2024年9月6日
# 描述：
# 该脚本适用于成都工业职业技术学院(东校区)校园网认证,简称 CISE
# 脚本带有日志记录功能，日志一般放于/var/log/cis/${nic}.log中
# #{nic} 为执行脚本时输入的nic=网卡名
# 脚本固定执行格式为 "bash 脚本路径 nic=网卡名 username=学号 password=身份证后6位"
# 需配合 kmod-macvlan watchcat mwan3 及 21.03 或以上OpenWrt版本使用
# 注意事项：
# 1. 校园认证猜测为RuiJie的Portal认证系统
# 2. 认证格式随时会发生改变，若发生改变请自行抓包分析，并修改 $content 变量内容
# 3. 日志记录并不带分割、定时删除等功能，请注意日志占用。[Info] 为正常记录信息 [Error] 为错误信息
# 4. 脚本仍然达不到我的需求，还需要其它插件的辅助，目前已经在开发OpenWrt插件,


# ===== declare variable =====
# 连通性测试IP，若默认的地址不再提供ICMP访问，请切换其它地址
connect_test_addr="223.5.5.5"

# curl 命令超时时间
# 单位为秒
timeout_second="5"

# ping 命令次数
ping_times="8"

# 日志最大大小
log_size_max="102400"

# 认证设备
# 移动端填2
# PC端填1
# 建议在路由器上只使用移动端
# PC端需要在教室上课时使用
device="2"

# 请不要修改以下变量，变量会在后面赋值
username=""
password=""
nic=""
log_file=""
user_agent=""

# ===== function =====

# print help prompt
printHelp() {
    echo "Help Prompt - Cdivtc WebAuth Script"
	
	echo "    Option Format - <key=value>"
    echo "        <nic> - Network Interface Card Name"
    echo "        <username> - WebAuth Account 'School ID'"
    echo "        <password> - WebAuth Password 'School ID' password'"
}

check_log_size() {
	local log_dir="/var/log/cise"
	local log_path="${log_dir}/${log_file}"
    local og_file_size=$(stat --format=%s /var/log/cise/eth0mac0.log)

    if [ ${og_file_size} -ge ${log_size_max} ]; then
        rm ${log_path}
    fi
}

# argument 1: log content
echoLog() {
    local date_time=$(date "+%Y/%m/%d %H:%M:%S")
	local log_dir="/var/log/cise"
	local log_path="${log_dir}/${log_file}"

	if [ ! -d ${log_dir} ]; then
	    mkdir -p ${log_dir}
	fi

    if [ ! -e ${log_path} ]; then
        touch ${log_path}
    fi

    check_log_size

    echo "[${date_time}] $1" >> "${log_path}"    
}

# connectivity test
# return 0 or 1
connectTest() {
    local nic=$1
    
    ping -I ${nic} ${connect_test_addr} -q -c ${ping_times} > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        return 0
    fi
    
    return 1
}

# ===== 参数识别 =====
optionParse() {
	if (( $# < 3 )); then
		printHelp
		exit 0
	fi

	local option=""
	local value=""
	

	for a in $@
	do
    	option=$(echo "$a" | cut -d "=" -f 1)
		value=$(echo "$a" | cut -d "=" -f 2)
		# 确保参数按照 key=value的格式正确传入
		# 该 if 判断用以确定 value 的值是否有效
		if [ -z "${value}" ];then
			printHelp
			exit 1
		fi

		# 该 case 用以确定 key 的值是否有效
		# 参数的具体值无需校验
		case $option in
			"username")
				username=$value
			;;
			"password")
				password=$value
			;;
			"nic")
				nic=$value
			;;
			*)
				printHelp
			;;
		esac
	done
}

optionParse $@

# 日志的划分通过接口名
log_file="${nic}.log"

echoLog "[Info] <${nic}> Starting Auth"

# 接口是否存在
link_dev=$(ip address show dev ${nic} 2> /dev/null)
if [ "$?" -ne "0" ]; then
    echoLog "[Error] ${nic} does not exist"
    exit 1
fi

# 网卡存在则获取IP和MAC
# 不要动下面的awk语法，除非你知道你自己在做什么
mac=$(echo "${link_dev}" | awk '/link\/ether/ {print $2}')

ip=$(echo "${link_dev}" | awk '/inet / {print $2}' | cut -d '/' -f 1)

# 上文中已经检查了网卡是否存在
# 若下面检测ip出现空的情况
# 说明你的网卡没有成功启动，并获取IP
# 我的建议是反复重启，因为openwrt的整个系统配置
# 均由 uci 来进行管理，很有可能是没有成功写入
if [ -z "${ip}" ];then
    echoLog "[Error] IP is null"
	exit 1
fi

# Testing connectivity
# 连通性检测，若该网卡能够成功联网，那么说明网卡已经成功认证
# 可以跳过后面的步骤
connectTest ${nic}
if (( $? == 0 )); then
    echoLog "[Info]Nic is connected internet"
    exit 0
fi

# built url
url="http://172.16.4.32/webauth.do?wlanuserip=${ip}&wlanacname=bras&wlanusermac=${mac}"

# ===== Echo URL =====
echoLog "[Info] URL that has already been built: ${url}"

# user-agent built
case ${device} in
    "1")
		user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
		content="hostIp=http://127.0.0.1:8083&loginType=&auth_type=0&isBindMac1=0&pageid=1&templatetype=1&listbindmac=0&recordmac=0&isRemind=1&loginTimes=&groupId=&distoken=&echostr=&url=&isautoauth=&notice_pic_loop1=/portal/uploads/pc/demo3/images/logo.jpg&notice_pic_loop2=/portal/uploads/pc/demo3/images/rrs_bg.jpg&userId=${username}&passwd=${password}"
	;;
	"2")
		user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
		content="hostIp=http://127.0.0.1:8080&loginType=&auth_type=0&isBindMac1=0&pageid=2&templatetype=2&listbindmac=0&recordmac=0&isRemind=0&loginTimes=&groupId=&distoken=&echostr=&url=&isautoauth=&notice_pic_loop1=/portal/uploads/mobile/demo3/images/logo.jpg&userId=${username}&passwd=${password}"
	;;
	*)
	    echoLog "[Error] The device type is error"
		exit 1
	;;
esac

# Auth Request Body
# 经过多次测试，关键参数仅为3个：
# 1. pageid 用以确定认证端设备类型
# 2. userId 和 passwd 无需多言

# ===== Echo Body =====

echoLog "[Info] Body that has already been built: ${content}"

# ===== Do webauth =====

# Auth Request
# 校园网认证成功后会有一个重定向
# 但该重定向无法定位成功
# 特使用--max-time超时时间配置
# 用以结束curl请求加载
status_code=$(curl -A "${user_agent}" -X POST -H "${header}" -Ls -o "/dev/null" -w "%{http_code}\n" --max-time "${timeout_second}" --interface "${nic}" -d "${content}" "$url")

# 记录返回状态码，用以调试
# 如果返回 200，说明认证失败了
# 因为200说明页面加载成功
# 正常来说认证成功后会请求 /portal/js/connect.succ.deal.js
# 用以获取联网成功检测的地址
# 在目前为止，测试的地址，无法加载，所以会出现重定向timeout的情况
echoLog "[Info] HTTP CODE ${status_code}"

# 测试网络是否认证成功
# 就算返回的不是200，也并不能百分百确定
# 确实是认证成功了
# 所以这里再做一遍连通性检测
connectTest ${nic}
if [ $? -eq 0 ];then
    echoLog "[Info] Online IP: ${ip} MAC: ${mac}"
else
    echoLog "[Error] UnOnlie"
fi

