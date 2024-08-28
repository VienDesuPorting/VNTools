import os.path
from argparse import Namespace, ArgumentParser
from dataclasses import dataclass
from typing import Any
import tomllib


@dataclass
class Config:

    config: dict[str, Any]
    args: Namespace

    @classmethod
    def setup_config(cls):
        parser = ArgumentParser(prog="vnrecode",
                                description="Python utility to compress Visual Novel Resources"
                                )
        parser.add_argument("source")
        parser.add_argument("-c", "--config", default="vnrecode.toml")
        args = parser.parse_args()
        if os.path.isfile(args.config):
            with open(args.config, "rb") as cfile:
                config = tomllib.load(cfile)
        else:
            print("Failed to find config. Check `vnrecode -h` to more info")
            exit(255)
        return cls(config=config, args=args)
