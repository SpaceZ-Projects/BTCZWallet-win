
import os
import sys
import ssl
import shutil
import zipfile
import subprocess
import urllib.request


def compare_versions(v1, v2):
    """Compares two version strings."""
    def normalize(version):
        return [int(x) for x in version.split(".")]
    v1_parts = normalize(v1)
    v2_parts = normalize(v2)
    while len(v1_parts) < len(v2_parts): v1_parts.append(0)
    while len(v2_parts) < len(v1_parts): v2_parts.append(0)
    return (v1_parts > v2_parts) - (v1_parts < v2_parts)


def run_subprocess(command, **kwargs):
    """Run a subprocess command and handle errors."""
    try:
        subprocess.check_call(command, **kwargs)
    except subprocess.CalledProcessError:
        print(f"[ERROR] Command failed: {' '.join(command)}")
        sys.exit(1)


def get_python_versions():
    """List installed Python versions (3.9 or newer)."""
    versions = set()
    try:
        output = subprocess.check_output(["py", "--list"], stderr=subprocess.DEVNULL).decode()
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("-V:"):
                version = line.split(":")[1].strip().split()[0]
            elif line.startswith("-"):
                version = line[1:].split("-")[0].strip()
            else:
                continue
            if compare_versions(version, "3.9") >= 0:
                versions.add(version)
    except subprocess.CalledProcessError:
        print("[ERROR] Unable to retrieve Python versions.")
    return sorted(versions)


def select_python_version():
    """Prompt user to choose a Python version."""
    versions = get_python_versions()
    if not versions:
        print("[ERROR] No Python 3.9+ version found. Please install one.")
        sys.exit(1)

    print("\nAvailable Python Versions:")
    for i, version in enumerate(versions, 1):
        print(f"{i}. Python {version}")

    try:
        choice = int(input("Select a Python version by number: "))
        if 1 <= choice <= len(versions):
            return versions[choice - 1]
        raise ValueError
    except ValueError:
        print("[ERROR] Invalid selection.")
        sys.exit(1)


def create_virtualenv(env_name, python_version):
    print(f"[INFO] Creating virtual environment (Python {python_version})...")
    run_subprocess(["py", f"-{python_version}", "-m", "venv", env_name])


def upgrade_pip(env_path):
    print("[INFO] Upgrading pip...")
    run_subprocess([os.path.join(env_path, 'Scripts', 'python.exe'), "-m", "pip", "install", "--upgrade", "pip"])


def install_briefcase(env_path):
    print("[INFO] Installing Briefcase...")
    run_subprocess([os.path.join(env_path, 'Scripts', 'pip'), "install", "briefcase==0.3.24"])


def ensure_briefcase_installed(env_path):
    pip_path = os.path.join(env_path, 'Scripts', 'pip')
    result = subprocess.run([pip_path, "show", "briefcase"], stdout=subprocess.DEVNULL)
    if result.returncode != 0:
        install_briefcase(env_path)


def prompt_operation():
    options = {
        1: "Build Installer",
        2: "Build Portable",
        3: "Run Application"
    }

    print("\nAvailable Operations:")
    for key, desc in options.items():
        print(f"{key}. {desc}")

    try:
        choice = int(input("Select an operation: "))
        if choice in options:
            return choice
        raise ValueError
    except ValueError:
        print("[ERROR] Invalid operation.")
        sys.exit(1)


def build_app(env_path):
    print("[INFO] Building application...")
    if os.path.exists("build"):
        print("[INFO] Cleaning previous build...")
        shutil.rmtree("build")

    run_subprocess([os.path.join(env_path, 'Scripts', 'briefcase'), "build"])
    shutil.rmtree("icons", ignore_errors=True)


def run_app(env_path):
    print("[INFO] Launching app in development mode...")
    run_subprocess([os.path.join(env_path, 'Scripts', 'briefcase'), "dev"])


def build_portable(env_path):
    print("[INFO] Packaging application as portable ZIP...")
    run_subprocess([os.path.join(env_path, 'Scripts', 'briefcase'), "package", "-p", "zip"])
    shutil.rmtree("icons", ignore_errors=True)


def download_nsis():
    nsis_dir = os.path.join("nsis", "nsis-3.10")
    makensis_path = os.path.join(nsis_dir, "makensis.exe")

    if os.path.exists(makensis_path):
        print("[INFO] NSIS is already installed.")
        return

    print("[INFO] Downloading NSIS...")
    url = "https://sourceforge.net/projects/nsis/files/NSIS%203/3.10/nsis-3.10.zip/download"
    zip_file = "nsis-3.10.zip"
    context = ssl._create_unverified_context()

    with urllib.request.urlopen(url, context=context) as response, open(zip_file, 'wb') as f:
        f.write(response.read())

    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall("nsis")

    os.remove(zip_file)
    print("[INFO] NSIS downloaded and extracted.")


def build_installer():
    makensis = os.path.join("nsis", "nsis-3.10", "makensis.exe")
    script_file = "btczwallet.nsi"

    if not os.path.exists(makensis):
        print("[ERROR] NSIS compiler not found.")
        sys.exit(1)

    print("[INFO] Compiling installer...")
    run_subprocess([makensis, script_file])


def main():
    env_path = "env"

    if not os.path.exists(env_path):
        python_version = select_python_version()
        create_virtualenv(env_path, python_version)
        upgrade_pip(env_path)

    ensure_briefcase_installed(env_path)
    operation = prompt_operation()

    if operation == 1:
        build_app(env_path)
        download_nsis()
        build_installer()
    elif operation == 2:
        build_portable(env_path)
    elif operation == 3:
        run_app(env_path)
    if operation != 3:
        input("\n[INFO] Operation complete. Press Enter to exit...")


if __name__ == "__main__":
    main()