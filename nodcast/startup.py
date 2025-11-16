from pathlib import Path
import shutil
import importlib.resources as res
import os
import platform
import yaml
import shutil

def read_new_yaml():
    """
    Read 'new.yaml' file from the parent of the 'nodcast' package's 'resources' directory
    and return its parsed YAML content.
    """
    try:
        # Locate the parent directory of the 'nodcast' package
        parent_path = res.files("nodcast").parent
        yaml_path = parent_path / "docs" / "new.yaml"

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

def copy_examples_to_docs(profile="default", doc_path=None):
    if doc_path is None:
        doc_path = get_documents_path("nodcast", as_str=False)
    else:
        doc_path = Path(doc_path)

    dest = doc_path / profile

    try:
        # Access packaged examples directly from importlib.resources
        examples_root = res.files("nodcast") / "docs" / "examples"

        # Convert to a real filesystem path (works even if in a zip)
        with res.as_file(examples_root) as tmp_dir:
            src_dir = Path(tmp_dir)

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

