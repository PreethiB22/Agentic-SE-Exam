
import json
import urllib.request
import urllib.error

from packaging.specifiers import SpecifierSet
from packaging.version import Version


PYTHON_VERSION = "3.11"


def check_package(package, version):

    url = f"https://pypi.org/pypi/{package}/{version}/json"

    try:
        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode("utf-8"))

        # Get Python version requirement
        requires_python = data["info"]["requires_python"]

        return requires_python

    except urllib.error.HTTPError:
        return None

    except Exception:
        return None


def get_minimum_python_version(requirement):

    specifiers = SpecifierSet(requirement)

    minimum = None

    for spec in specifiers:

        if spec.operator in (">=", ">", "~=", "=="):

            if "*" in spec.version:
                continue

            version = Version(spec.version)

            if minimum is None or version > minimum:
                minimum = version

    return minimum


def main():

    # Read requirements.txt
    with open("requirements.txt", "r") as file:
        lines = file.readlines()

    dependencies_checked = len(lines)

    not_found = 0
    incompatible = 0

    highest_package = None
    highest_version = None
    highest_requirement = None
    highest_minimum = None

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Separate package name and version
        package, version = line.split("==")

        # Check package on PyPI
        requires_python = check_package(package, version)

        # Package or pinned version does not exist
        if requires_python is None:
            not_found += 1
            continue

        # Check Python compatibility
        if requires_python:

            specifiers = SpecifierSet(requires_python)

            if not specifiers.contains(PYTHON_VERSION):
                incompatible += 1

            # Find highest minimum Python requirement
            minimum = get_minimum_python_version(
                requires_python
            )

            if minimum is not None:

                if highest_minimum is None or minimum > highest_minimum:

                    highest_minimum = minimum
                    highest_package = package
                    highest_version = version
                    highest_requirement = requires_python

    print("Dependencies checked:", dependencies_checked)

    print("Not found on PyPI:", not_found)

    print("Incompatible with Python 3.11:", incompatible)

    if highest_package is not None:

        print(
            "Highest requirement:",
            f"{highest_package}=={highest_version}",
            f"({highest_requirement})"
        )


if __name__ == "__main__":
    main()
