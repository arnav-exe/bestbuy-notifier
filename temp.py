import subprocess
import sys


def main():
    if sys.platform == "win32":
        subprocess.run(["npx.cmd", "amazon-buddy"])
    else:
        subprocess.run(["npx", "amazon-buddy"])


if __name__ == "__main__":
    main()
