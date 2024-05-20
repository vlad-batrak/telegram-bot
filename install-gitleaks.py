import os
import platform
import subprocess
import sys
import zipfile

version = "v8.18.2"


def is_gitleaks_installed():
    """Check if gitleaks is installed."""
    try:
        subprocess.run(['gitleaks', 'version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def download_and_install_gitleaks():
    """Generate the download URL for gitleaks based on the OS and architecture."""
    os_type = platform.system().lower()
    arch = platform.architecture()[0].lower()
    mach = platform.machine().lower()

    if arch == "64bit":
        arch = "x64"
    elif arch == "32bit":
        arch = "x32"
    elif mach in ["aarch64", "arm64"]:
        arch = "arm64"
    elif mach in ["armv7l", "armv7"]:
        arch = "armv7"
    elif mach in ["armv6l", "armv6"]:
        arch = "armv6"
    else:
        raise Exception(f"Unsupported architecture: {arch}")

    base_url = f"https://github.com/gitleaks/gitleaks/releases/download/{version}"
    file_name = f"gitleaks_{version[1:]}_{os_type}_{arch}"
    url = f"{base_url}/{file_name}"

    if os_type == "linux" or os_type == "darwin":
        try:
            subprocess.run(f"curl -sSfL {url}.tar.gz -o gitleaks.tar.gz", shell=True, check=True)
            subprocess.run("tar -xzf gitleaks.tar.gz gitleaks", shell=True, check=True)
            subprocess.run("chmod +x gitleaks", shell=True, check=True)
            subprocess.run("sudo mv gitleaks /usr/local/bin/gitleaks", shell=True, check=True)
            os.remove("gitleaks.tar.gz")
            print("Gitleaks installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error during installation: {e}")
            sys.exit(1)
    elif os_type == "windows":
        try:
            subprocess.run(f"curl -sSfL {url}.zip -o gitleaks.zip", shell=True, check=True)
            
            with zipfile.ZipFile("gitleaks.zip", 'r') as zip_ref:
                zip_ref.extractall("gitleaks")
            
            gitleaks_path = os.path.join("gitleaks", "gitleaks.exe")
            destination_path = os.path.join(os.getenv('ProgramFiles'), 'gitleaks', 'gitleaks.exe')
            
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            os.rename(gitleaks_path, destination_path)
            
            if destination_path not in os.getenv('PATH'):
                os.environ['PATH'] += os.pathsep + os.path.dirname(destination_path)

            os.remove("gitleaks.zip")
            os.rmdir("gitleaks")
            
            print("Gitleaks installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error during installation: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"General error during installation: {e}")
            sys.exit(1)
    else:
        print(f"Unsupported OS: {os_type}")
        sys.exit(1)


def check_gitleaks_hook_enabled():
    try:
        result = subprocess.run(
            ['git', 'config', '--bool', 'hooks.gitleaks'],
            capture_output=True,
            text=True,
            check=True
        )

        gitleaks_hook_enabled = result.stdout.strip()
        
        if gitleaks_hook_enabled != "true":
            print("Gitleaks pre-commit hook is disabled. Enable it by running:")
            print("git config hooks.gitleaks true")
            sys.exit(1)
        else:
            sys.exit(0)
    except subprocess.CalledProcessError:
        print("Error checking git configuration.")
        sys.exit(1)


if __name__ == "__main__":
    if not is_gitleaks_installed():
        try:
            download_and_install_gitleaks()
        except Exception as e:
            print(f"Installation failed: {e}")
            sys.exit(1)

    if check_gitleaks_hook_enabled():
        try:
            result = subprocess.run("gitleaks detect --source . --redact", shell=True, check=True)
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, result.args)
            sys.exit(0)
        except subprocess.CalledProcessError:
            print("Gitleaks detected sensitive information. Please review and fix.")
            sys.exit(1)
