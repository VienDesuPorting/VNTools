class Printer:

    @staticmethod
    def info(msg: str):
        print(f"\033[100m[INFO] {msg}\033[49m")

    @staticmethod
    def warn(msg: str):
        print(f"\033[93m[WARN]\033[0m {msg}\033[49m")

    @staticmethod
    def err(msg: str):
        print(f"\033[31m[ERROR]\033[0m {msg} Exiting...\033[49m")
        exit()
