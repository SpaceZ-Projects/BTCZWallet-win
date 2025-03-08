
import os
import subprocess
import sys
import urllib.request
import ssl
import zipfile
import shutil


def check_git_installed():
    try:
        subprocess.check_call(
            ["git", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError:
        print("Git is not installed. Installing Git...")
        install_git()


def install_git():
    git_installer_url = "https://git-scm.com/download/win"
    print(f"Please install Git by downloading from: {git_installer_url}")


def compare_versions(version1, version2):
    v1_parts = [int(x) for x in version1.split('.')]
    v2_parts = [int(x) for x in version2.split('.')]

    while len(v1_parts) < len(v2_parts):
        v1_parts.append(0)
    while len(v2_parts) < len(v1_parts):
        v2_parts.append(0)

    if v1_parts > v2_parts:
        return 1
    elif v1_parts < v2_parts:
        return -1
    return 0


def get_python_versions():
    versions = []
    try:
        output = subprocess.check_output(["py", "--list"])
        for line in output.decode().splitlines():
            if line.startswith(" -V:"):
                version_str = line.split(":")[1].split()[0]
                if compare_versions(version_str, "3.9") >= 0:
                    versions.append(version_str)
            elif line.startswith(" -"):
                version_str = line.split('-')[1].split()[0]
                if compare_versions(version_str, "3.9") >= 0:
                    versions.append(version_str)
    except subprocess.CalledProcessError:
        print("Could not find Python versions.")
    return versions

def select_python_version():
    versions = get_python_versions()
    if not versions:
        print("No Python versions found. Please install a version of Python.")
        sys.exit(1)

    print("Select a Python version:")
    for idx, version in enumerate(versions, start=1):
        print(f"{idx}. {version}")

    choice = int(input("Enter the number corresponding to your choice: "))
    if 1 <= choice <= len(versions):
        return versions[choice - 1]
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)

def operation_choice():
    print("Select a operation:")
    print("0. build app")
    print("1. run app")
    choice = int(input("Enter the number corresponding to your choice: "))
    if choice == 0:
        return 0
    elif choice == 1:
        return 1
    else:
        print("Invalid choice! Please select 0 or 1.")
        sys.exit(1)


def create_virtualenv(env, python_version):
    print(f"Creating virtual environment with Python {python_version}...")
    subprocess.check_call(
        ["py", f"-{python_version}", "-m", "venv", env]
    )

def upgrade_pip(env):
    print(f"Upgrading pip...")
    subprocess.check_call(
        [os.path.join(env, 'Scripts', 'python.exe'), "-m", "pip", "install", "--upgrade", "pip"]
    )

def install_briefcase(env):
    print(f"Installing Briefcase...")
    subprocess.check_call(
        [os.path.join(env, 'Scripts', 'pip'), "install", "briefcase"]
    )

def build_app(env):
    print(f"Building App...")
    build_dir = "build"
    if os.path.exists(build_dir):
        print("Deleting existing build directory...")
        shutil.rmtree(build_dir)
    subprocess.check_call(
        [os.path.join(env, 'Scripts', 'briefcase'), "build"]
    )

def run_app(env):
    print(f"Running App...")
    subprocess.check_call(
        [os.path.join(env, 'Scripts', 'briefcase'), "dev"]
    )

def download_nsis():
    nsis_dir = os.path.join("nsis", "nsis-3.10", "makensis.exe")
    if os.path.exists(nsis_dir):
        print("NSIS is already installed. Skipping...")
        return

    print("Downloading NSIS...")
    nsis_url = "https://sourceforge.net/projects/nsis/files/NSIS%203/3.10/nsis-3.10.zip/download"
    nsis_zip = "nsis-3.10.zip"
    nsis_extract_dir = "nsis"
    context = ssl._create_unverified_context()

    with urllib.request.urlopen(nsis_url, context=context) as response, open(nsis_zip, 'wb') as out_file:
        out_file.write(response.read())
    with zipfile.ZipFile(nsis_zip, 'r') as zip_ref:
        zip_ref.extractall(nsis_extract_dir)
    os.remove(nsis_zip)
    print(f"NSIS extracted to {nsis_extract_dir}")


def build_installer():
    print("Building the installer using NSIS...")
    nsis_script = "btczwallet.nsi"
    nsis_compiler = os.path.join("nsis", "nsis-3.10", "makensis.exe")

    if not os.path.exists(nsis_compiler):
        print("NSIS is not installed. Please install it first.")
        sys.exit(1)
    subprocess.check_call([nsis_compiler, nsis_script])


def main():
    check_git_installed()
    env = "env"

    if not os.path.exists(env):
        python_version = select_python_version()
        create_virtualenv(env, python_version)
        upgrade_pip(env)

    operation = operation_choice()

    try:
        subprocess.check_call(
            [os.path.join(env, 'Scripts', 'pip'), "show", "briefcase"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError:
        install_briefcase(env)

    if operation == 0:
        build_app(env)
        download_nsis()
        build_installer()
        
    elif operation == 1:
        run_app(env)

if __name__ == "__main__":
    main()
