#!/usr/bin/env zsh
echo "version bump"
poetry version patch || exit 1
current_version=$(poetry version -s) || exit 1
package_name=$(poetry version | cut -d ' ' -f 1)
sed -i '' "s/__version__ = \".*\"/__version__ = \"$current_version\"/" version.py || exit 1

git add --all || exit 1
git commit -m "Bump version to $current_version and update version.py" || exit 1
git tag v$current_version || exit 1
git push origin main || exit 1
git push origin v$current_version || exit 1

echo "build"
poetry lock && poetry install || exit 1
poetry build --clean || exit 1

echo "publish to PyPI"
poetry publish || exit 1

echo "wait for PyPI propagation"
sleep 10

echo "uninstall existing versions"
pipx uninstall $package_name

echo "install from PyPI"
pip install --upgrade $package_name==$current_version || exit 1
pipx install $package_name==$current_version --force || exit 1

echo "check installations"
echo "pip list:"
pip list | grep $package_name
echo "pipx list:"
pipx list | grep $package_name
