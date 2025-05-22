#!/usr/bin/env zsh
print-divider "version bump"
poetry version patch || exit 1
current_version=$(poetry version -s) || exit 1
package_name=$(poetry version | cut -d ' ' -f 1)
sed -i '' "s/__version__ = \".*\"/__version__ = \"$current_version\"/" version.py || exit 1
# git add --all || exit 1
# git commit -m "Bump version to $current_version and update version.py" || exit 1
git-fix
print-divider "build"
poetry lock && poetry install || exit 1
poetry build --clean || exit 1
# print-divider "uninstall"
# pipx uninstall $package_name
# print-divider "pipx install"
# pipx install ./dist/validated_llm-$current_version*.whl --force || exit 1
print-divider "pip install"
pip install -e . || exit 1
# print-divider "pipx list"
# pipx list | grep $package_name
print-divider "pip list"
pip list --editable | grep $package_name
