from pathlib import Path
import shutil
import os
import platform
import yaml
import shutil
import nodcast

# Compatibility import
try:
    import importlib.resources as res
    from importlib.resources import files, as_file
except ImportError:
    import importlib_resources as res
    from importlib_resources import files, as_file    # Python < 3.9 fallback

def get_examples_path():
    pkg_path = Path(nodcast.__file__).parent
    return pkg_path / "docs" / "examples"


def copy_examples_to_docs(profile="default", doc_path=None):
    """
    Copy packaged example files from nodcast/docs/examples into the user's docs folder.
    Uses file-based path discovery instead of importlib.resources to ensure
    compatibility on Windows, Linux, editable installs, and packaged installs.
    """

    if doc_path is None:
        doc_path = get_documents_path("nodcast", as_str=False)
    else:
        doc_path = Path(doc_path)

    dest = doc_path / profile

    try:
        # Locate the installed package root using this file's location
        package_root = Path(__file__).resolve().parent
        examples_root = package_root / "docs" / "examples"

        if not examples_root.exists():
            print("No examples found in package.")
            return

        dest.mkdir(parents=True, exist_ok=True)
        copied_any = False

        for item in examples_root.rglob("*"):
            rel = item.relative_to(examples_root)
            target = dest / rel

            if item.is_dir():
                target.mkdir(exist_ok=True)
            else:
                if not target.exists():
                    shutil.copy2(item, target)
                    copied_any = True

        if copied_any:
            print(f"Example files copied to {dest}")
        else:
            print(f"Examples already exist in {dest}, no files copied.")

    except Exception as e:
        print(f"Failed to copy examples: {e}")

def copy_examples_to_docs_2(profile="default", doc_path=None):
    if doc_path is None:
        doc_path = get_documents_path("nodcast", as_str=False)
    else:
        doc_path = Path(doc_path)

    dest = doc_path / profile

    try:
        examples_root = files("nodcast") / "docs" / "examples"

        with as_file(examples_root) as src_dir:
            src_dir = Path(src_dir)

            if not src_dir.exists():
                print("No examples found in package.")
                return

            dest.mkdir(parents=True, exist_ok=True)
            copied_any = False

            for item in src_dir.rglob("*"):
                rel = item.relative_to(src_dir)
                target = dest / rel

                if item.is_dir():
                    target.mkdir(exist_ok=True)
                else:
                    if not target.exists():
                        shutil.copy2(item, target)
                        copied_any = True

            if copied_any:
                print(f"Example files copied to {dest}")
            else:
                print(f"Examples already exist in {dest}, no files copied.")

    except Exception as e:
        print(f"Failed to copy examples: {e}")


def read_new_yaml():
    """
    Read 'new.yaml' file from the parent of the 'nodcast' package's 'resources' directory
    and return its parsed YAML content.
    """
    try:
        # Locate the parent directory of the 'nodcast' package
        # res_path = res.files("nodcast")
        # yaml_path = res_path / "docs" / "new.yaml"

        package_root = Path(__file__).resolve().parent
        yaml_path = package_root / "docs" / "new.yaml"

        with res.as_file(yaml_path) as actual_yaml_path:
            if not actual_yaml_path.exists():
                raise FileNotFoundError(f"'new.yaml' not found at {actual_yaml_path}")
            with open(actual_yaml_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)

    except Exception as e:
        print(f"Error reading new.yaml: {e}")
        return None


def get_documents_path(appname="nodcast", as_str=True):
    """Return cross-platform Documents/<appname> path and create it."""
    if platform.system() == "Windows":
        doc_base = Path(os.path.join(os.environ.get("USERPROFILE", ""), "Documents"))
    else:
        doc_base = Path.home() / "Documents"
    path = doc_base / appname
    path.mkdir(parents=True, exist_ok=True)
    return str(path) if as_str else path

def get_profiles(doc_path=None, profile_str="profile:"):
    if doc_path is None:
        doc_path = get_documents_path("nodcast", as_str=False)
    else:
        doc_path = Path(doc_path)

    # Scan directories under doc_path
    profiles = []
    if doc_path.exists():
        for entry in doc_path.iterdir():
            if entry.is_dir() and entry.name not in ("__pycache__"):
                # For example, each folder could represent a user profile
                profiles.append(entry.name)

    return profiles

