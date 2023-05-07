import argparse

class MyClass:
    def __init__(self, arg1, arg2):
        self.arg1 = arg1
        self.arg2 = arg2
        print(f"MyClass initialized with arg1={arg1} and arg2={arg2}")


parser = argparse.ArgumentParser(description="Pass arguments to MyClass")

parser.add_argument('--arg1', type=int, required=False, help="Argument 1 for MyClass")
parser.add_argument('--arg2', type=str, required=False, help="Argument 2 for MyClass")

args = parser.parse_args()

my_instance = MyClass(args.arg1, args.arg2)