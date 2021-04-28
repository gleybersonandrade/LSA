"""LSA main function"""

# System imports
import argparse

# Local imports
from files import *
from lsa import *
from utils import *


def main():
    parser = argparse.ArgumentParser(description='LSA')
    parser.add_argument('-p', '--project', required=True)
    parser.add_argument('-g', '--generate')
    parser.add_argument('-i', '--input')
    parser.add_argument('-t', '--type', default='original')
    args = parser.parse_args()

    if args.generate:
        features = collect_features(args.generate)
        model = generate_model(features)
        write_file(features, f"features/{args.project}.json")
        write_file(model, f"in/{args.project}.json")
    elif args.input:
        model = read_file(args.input)
        data = globals()[args.type](model)
        write_file(data, f"out/{args.project}_{args.type}.json")
        show_results(data)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
