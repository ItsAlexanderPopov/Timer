import subprocess
import sys
import os

def run_command(command):
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

    for line in process.stdout:
        print(line, end='')

    process.wait()
    return process.returncode

def build_executable():
    venv_python = sys.executable
    output_filename = "Timer.exe"

    command = [
        venv_python,
        "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--windows-console-mode=disable",
        "--plugin-enable=pyside6",
        "--include-package=keyboard",
        "--include-package=psutil",
        "--windows-icon-from-ico=icon.ico",
        "--assume-yes-for-downloads",
        "--disable-console",
        "--company-name=AlexPopov",
        "--product-name=Timer",
        "--file-version=1.0.0",
        "--product-version=1.0.0",
        "--copyright=Copyright©2024.",
        "--windows-disable-console",
        "--remove-output",
        "--no-pyi-file",
        "--no-prefer-source-code",
        "--static-libpython=no",
        "--disable-ccache",
        "--nofollow-import-to=tkinter,matplotlib",
        "--no-deployment-flag=uses-tkinter",
        "--include-data-file=sound.wav=sound.wav",
        "--output-filename=%s" % output_filename,
        "main.py"
    ]

    print(f"Using Python interpreter: {venv_python}")
    print(f"Executing command: {' '.join(command)}")

    return_code = run_command(command)

    if return_code != 0:
        print(f"Build failed with return code {return_code}")
    else:
        print("Build completed successfully.")
        if os.path.exists(output_filename):
            size_mb = os.path.getsize(output_filename) / (1024 * 1024)
            print(f"\nFinal executable size: {size_mb:.2f} MB")
        else:
            print(f"Warning: {output_filename} not found.")

if __name__ == "__main__":
    build_executable()