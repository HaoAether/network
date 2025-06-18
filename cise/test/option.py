import argparse as ag

parser = ag.ArgumentParser(prog="cise", description="cise - Chengdu Industry Student Enabler (v1.0)")

config_group = parser.add_argument_group(title="config options")

# 当 -u -p -i 存在时，-c 不生效
config_group.add_argument("-u", "--username", help="username", required=False)
config_group.add_argument("-p", "--password", help="password", required=False)
config_group.add_argument("-i", "--interface", help="interface", required=False)

# 当 -c 存在时，-u -p -i 不生效
# config_group.add_argument("-c", "--config", help="config file", required=False)

# 当 -o 存在时，只有 -c 能够被使用
# parser.add_argument("-o", "--openwrt", action="openwrt", help="use openwrt", required=False)


# 以下功能为调用后直接关闭
once_group = parser.add_argument_group(title="exiting after call")
once_group.add_argument("-v", action="version", version='%(prog)s 1.0') # 调用就退出
once_group.add_argument("-l", "--list-interfaces", action="store_false", help="list all interface in the system and exit", required=False) 

openwrt = parser.add_subparsers(title="openwrt")

openwrt.add_parser

openwrt_group = parser.add_argument_group(title="openwrt config option")
openwrt_group.add_argument("-c", "--config", help="config file", required=False)
openwrt_group.add_argument("-o", "--openwrt",  help="use openwrt", required=False)

args = parser.parse_args()

if args.config != None:
    # 读取config指定的配置文件
    pass

print(args.interface)
print(args.username)
print(args.password)
print(args.list_interfaces)

# flag: 
# option: 有名称有值
# position: 没有名称，只有值

# sys.argv = 参数值数组
# sys.args = 参数个数
# int main(int args, char**argv)
# ls -l -a -> flag 可选：它后面没有参数值，它代表的是一个选择，有则为真。当option后面没有参数时，可以简写 -la 
# 3 参数:filename -l -a
# ls -la -> ls -la
# paraser -> l a 

# action
# * `store`
# * `store_const` 和 `const` 参数连用,不连用会出现赋值为 None.
# * `store_false` 和 `store_true` 当出现这个option时，将该option对象的value设置为 false or true
# * `append`: 代表这个option对象所存储的值是一个列表,当出现这个option时，向列表中追加值
# * `append_const`
# * `extend`: 
# * `count`: 统计该option出现的次数
# * `version`: 展示版本信息

# const 
# 当选项存在时，但是没有指定值，Option 对象都为 const 指定的值

# default
# 当选项不存在时，给这个 Option 对象赋值为 defualt 指定的值

# nargs
# 指定该选项后多少个参数为该option的值列表.如果我们不使用 nargs 选项，option对象返回的是一个type对应类型的值(默认为 str)。使用后，nargs存在时，option对象返回的值就变为了一个列表。
# * `?`： 消耗后续一个值，产生一个Option对象。
#   * 如果没有值，将 Option 对象的值设置为 const
#   * 如果有Option,但是没有值，将 Option 对象的值设置为 default

# 
