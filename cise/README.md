# cise

成都工业职业技术学院(东校区)校园网认证脚本

> 该脚本并不能实现破解校园网认证，只是使用代码的方式去进行上网认证操作，仍然需要自行办理校园网

## 概述

* `webauth.sh`: Bash认证脚本
* `PyAuth.py`: Python 认证脚本

`webauth.sh` 认证脚本为原版，考虑到Shell脚本的兼容性不是很好，会出现某些命令无法执行的情况，所以另外开发了一套Python版本的认证脚本

## Features

* `-o | --openwrt`: 指定该系统为OpenWrt,将触发OpenWrt自动配置(换源、安装mwan3、watchdog、macvlan，配置虚拟接口等)
* `-u | --username`: 校园网账号
* `-p | --password`: 校园网密码
* `-i | --interface`: 认证接口
* `-l | --list-interfaces`: 列出当前系统支持的所有接口(当你不知道应该指定哪一个认证接口时使用)
* `-c | --config`: 指定json格式配置文件(当存在 -c 时，若命令指定了配置选项，将覆盖-c中的配置参数)
* `-h | --help`: 列出帮助

### openwrt

提取 `-c` 或 `-u -p -i` 指定的信息





