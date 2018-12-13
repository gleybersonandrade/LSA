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
    args = parser.parse_args()
    if args.input and args.output:
        features = read_file(args.input)
        data = {}        
        one_enabled(data, features)
        one_disabled(data, features)
        most_enabled_disabled(data, features)
        write_file(data, args.output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()