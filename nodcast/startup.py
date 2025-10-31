from pathlib import Path
import shutil
import importlib.resources as res
import os
import platform

def get_documents_path(appname="nodcast", as_str=False):
    """Return cross-platform Documents/<appname> path and create it."""
    if platform.system() == "Windows":
        doc_base = Path(os.path.join(os.environ.get("USERPROFILE", ""), "Documents"))
    else:
        doc_base = Path.home() / "Documents"
    path = doc_base / appname
    path.mkdir(parents=True, exist_ok=True)
    return str(path) if as_str else path


def copy_examples_to_docs(profile = "default", doc_path=None):
    """Copy packaged examples to user's Documents/nodcast/examples/, only if missing."""
    if doc_path is None:
        doc_path = get_documents_path("nodcast", as_str=False)
    else:
        doc_path = Path(doc_path)

    dest = doc_path / profile / "examples"

    try:
        # locate 'docs/examples' within installed package
        examples_pkg_path = res.files("nodcast").parent / "docs" / "examples"

        with res.as_file(examples_pkg_path) as src_dir:
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

