"""LSA main function"""

# System imports
import argparse

# Local imports
from utils import *
from files import *


def main():
    parser = argparse.ArgumentParser(description='LSA')
    parser.add_argument('-i', '--input')
    parser.add_argument('-o', '--output')
    parser.add_argument('-t', '--type', default='original')
    args = parser.parse_args()
    if args.input and args.output:
        model = read_file(args.input)
        data = globals()[args.type](model)
        write_file(data, args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
