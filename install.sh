#!/usr/bin/env zsh
echo "version bump"
poetry version patch || exit 1
current_version=$(poetry version -s) || exit 1
package_name=$(poetry version | cut -d ' ' -f 1)
sed -i '' "s/__version__ = \".*\"/__version__ = \"$current_version\"/" version.py || exit 1
# git add --all || exit 1
# git commit -m "Bump version to $current_version and update version.py" || exit 1
git-amend
echo "build"
poetry lock && poetry install || exit 1
poetry build --clean || exit 1
echo "pip install"
pip install -e . || exit 1
echo "pip list"
pip list --editable | grep $package_name
echo "pipx uninstall"
pipx uninstall $package_name
echo "pipx install"
pipx install ./dist/validated_llm-$current_version*.whl --force || exit 1
echo "pipx list"
pipx list | grep $package_name
