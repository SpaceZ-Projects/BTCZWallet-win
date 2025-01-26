import os
import subprocess
import sys


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
    input("Press enter to continue...")


def create_virtualenv(env):
    print(f"Python version: {sys.version}")
    print(f"Creating virtual environment...")
    subprocess.check_call(
        [sys.executable, "-m", "venv", env]
    )

def upgrade_pip(env):
    print(f"Upgrading pip...")
    subprocess.check_call(
        [os.path.join(env, 'Scripts', 'python'), "-m", "pip", "install", "--upgrade", "pip"]
    )

def install_briefcase(env):
    print(f"Installing Briefcase...")
    subprocess.check_call(
        [os.path.join(env, 'Scripts', 'pip'), "install", "briefcase"]
    )

def build_portable(env):
    print(f"Building Portable...")
    subprocess.check_call(
        [os.path.join(env, 'Scripts', 'briefcase'), "package", "-p", "zip"]
    )

def build_msi(env):
    print(f"Building MSI...")
    subprocess.check_call(
        [os.path.join(env, 'Scripts', 'briefcase'), "package", "-p", "msi"]
    )
    input("Press enter to continue...")


def main():
    check_git_installed()
    env = "env"
    
    if not os.path.exists(env):
        create_virtualenv(env)
    upgrade_pip(env)
    install_briefcase(env)
    build_portable(env)
    build_msi(env)

if __name__ == "__main__":
    main()
