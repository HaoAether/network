import argparse

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest='command')

# 创建需要两个选项的子命令
cmd_parser = subparsers.add_parser('special')
cmd_parser.add_argument('--option-a', required=True)
cmd_parser.add_argument('--option-b', required=True)

args = parser.parse_args()

if args.command == 'special' and (not args.option_a or not args.option_b):
    parser.error("special command requires both --option-a and --option-b")