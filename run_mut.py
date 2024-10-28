import os
import pathlib
import re
import sys

from mutpy import commandline

# pylint: skip-file

tests_folder = "tests/test_parsers"

target_folder = "/home/vladimir/projects/autostab/price_formation/parsers/vendors"

args = ["--coverage", "--colored-output", "--target", target_folder, "--unit-test"]

work_dir = str(pathlib.Path(__file__).parent.absolute())
tests_dir = f"{work_dir}{os.sep}{tests_folder}"

regex = re.compile("test*")

test_modules = [tests_dir + os.sep + name for name in os.listdir(tests_dir) if re.match(regex, name)]

args += test_modules
args += ["--runner", "pytest"]

sys.path.append(tests_dir)

sys.argv = args
commandline.main(args)
