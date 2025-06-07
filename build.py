
import os
import subprocess
import sys
import urllib.request
import ssl
import zipfile
import shutil


def check_git_installed():
    """Check if Git is installed."""
    try:
        subprocess.check_call(["git", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[ERROR] Git is not installed.")
        print("Please install Git from: https://git-scm.com/download/win")
        sys.exit(1)


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
    """Get installed Python versions (>= 3.9)."""
    versions = set()
    try:
        output = subprocess.check_output(["py", "--list"], stderr=subprocess.DEVNULL)
        for line in output.decode().splitlines():
            line = line.strip()
            if line.startswith("-V:"):
                version_str = line.split(":")[1].strip().split()[0]
            elif line.startswith("-"):
                parts = line[1:].split("-")
                version_str = parts[0].strip()
            else:
                continue

            if compare_versions(version_str, "3.9") >= 0:
                versions.add(version_str)
    except subprocess.CalledProcessError:
        print("Could not find Python versions.")
    return sorted(versions)


def select_python_version():
    """Prompt the user to select an available Python version."""
    versions = get_python_versions()
    if not versions:
        print("[ERROR] No suitable Python versions found. Please install Python 3.9 or newer.")
        sys.exit(1)

    print("\nAvailable Python Versions:")
    for i, version in enumerate(versions, start=1):
        print(f"{i}. Python {version}")

    try:
        choice = int(input("Select the number corresponding to your preferred Python version: "))
        if 1 <= choice <= len(versions):
            return versions[choice - 1]
        else:
            raise ValueError
    except ValueError:
        print("[ERROR] Invalid selection.")
        sys.exit(1)


def prompt_operation():
    """Prompt the user to choose an operation."""
    options = {
        1: "Build Installer",
        2: "Build Portable",
        3: "Run Application"
    }
    print("\nAvailable Operations:")
    for key, desc in options.items():
        print(f"{key}. {desc}")

    try:
        choice = int(input("Enter the number corresponding to your desired operation: "))
        if choice in options:
            return choice
        else:
            raise ValueError
    except ValueError:
        print("[ERROR] Invalid operation choice.")
        sys.exit(1)


def create_virtualenv(env_name, python_version):
    """Create a virtual environment using the specified Python version."""
    print(f"[INFO] Creating virtual environment with Python {python_version}...")
    subprocess.check_call(["py", f"-{python_version}", "-m", "venv", env_name])


def upgrade_pip(env_path):
    """Upgrade pip within the virtual environment."""
    print("[INFO] Upgrading pip...")
    subprocess.check_call([os.path.join(env_path, 'Scripts', 'python.exe'), "-m", "pip", "install", "--upgrade", "pip"])


def install_briefcase(env_path):
    """Install Briefcase into the virtual environment."""
    print("[INFO] Installing Briefcase...")
    subprocess.check_call([os.path.join(env_path, 'Scripts', 'pip'), "install", "briefcase"])


def ensure_briefcase_installed(env_path):
    """Ensure Briefcase is installed in the environment."""
    try:
        subprocess.check_call([os.path.join(env_path, 'Scripts', 'pip'), "show", "briefcase"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        install_briefcase(env_path)


def build_app(env_path):
    """Build the application using Briefcase."""
    print("[INFO] Building application...")
    build_dir = "build"
    if os.path.exists(build_dir):
        print("[INFO] Cleaning existing build directory...")
        shutil.rmtree(build_dir)
    subprocess.check_call([os.path.join(env_path, 'Scripts', 'briefcase'), "build"])


def run_app(env_path):
    """Run the application in development mode."""
    print("[INFO] Launching application in development mode...")
    subprocess.check_call([os.path.join(env_path, 'Scripts', 'briefcase'), "dev"])


def download_nsis():
    """Download and extract NSIS (if not already installed)."""
    nsis_exe = os.path.join("nsis", "nsis-3.10", "makensis.exe")
    if os.path.exists(nsis_exe):
        print("[INFO] NSIS already installed. Skipping download.")
        return

    print("[INFO] Downloading NSIS...")
    nsis_url = "https://sourceforge.net/projects/nsis/files/NSIS%203/3.10/nsis-3.10.zip/download"
    nsis_zip = "nsis-3.10.zip"
    extract_dir = "nsis"
    context = ssl._create_unverified_context()

    with urllib.request.urlopen(nsis_url, context=context) as response, open(nsis_zip, 'wb') as f:
        f.write(response.read())

    with zipfile.ZipFile(nsis_zip, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)

    os.remove(nsis_zip)
    print(f"[INFO] NSIS extracted to '{extract_dir}'")


def build_installer():
    """Compile the NSIS installer."""
    print("[INFO] Compiling NSIS installer...")
    nsis_script = "btczwallet.nsi"
    nsis_compiler = os.path.join("nsis", "nsis-3.10", "makensis.exe")

    if not os.path.exists(nsis_compiler):
        print("[ERROR] NSIS not found.")
        sys.exit(1)

    subprocess.check_call([nsis_compiler, nsis_script])


def build_portable(env_path):
    """Build a portable zip version of the application."""
    print("[INFO] Building portable application package...")
    subprocess.check_call([os.path.join(env_path, 'Scripts', 'briefcase'), "package", "-p", "zip"])


def main():
    check_git_installed()

    env_dir = "env"
    if not os.path.exists(env_dir):
        python_version = select_python_version()
        create_virtualenv(env_dir, python_version)
        upgrade_pip(env_dir)

    operation = prompt_operation()
    ensure_briefcase_installed(env_dir)

    if operation == 1:
        build_app(env_dir)
        download_nsis()
        build_installer()
    elif operation == 2:
        build_portable(env_dir)
    elif operation == 3:
        run_app(env_dir)


if __name__ == "__main__":
    main()