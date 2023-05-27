import os


def info(string):
    print(f"[INFO] \033[0;32m{string}\033[0m")


def files(progress, source, dest, dest_ext, comment):
    source_ext = os.path.splitext(source)[1]
    source_name= os.path.splitext(source)[0]

    if progress < 10:
        progress = f"  {progress}"
    elif progress < 100:
        progress = f" {progress}"

    print(f"[{progress}%] \033[0;32m{source_name}\033[0m{source_ext}\033[0;32m -> {dest}\033[0m.{dest_ext}\033[0;32m ({comment})\033[0m")


def warning(string):
    print(f"\033[0;33m[WARNING] {string}\033[0m")