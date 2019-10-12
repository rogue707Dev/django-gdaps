#!/usr/bin/env bash

die() {
    # die with a message
    echo " ✘ $1"
    exit 1
}

check_prereq(){
  if python -c "import pkgutil; exit(not pkgutil.find_loader('${1}'))" >/dev/null; then
      echo " ✓ ${1} found."
  else
      die "Missing dependency: Please install ${1} in this virtualenv."
  fi
}

#version=$(grep "version=" setup.py| cut -d '"' -f2)
version=$(grep "__version__" gdaps/__init__.py | cut -d '"' -f2)
[[ "$version" == "" ]] && die "Could not determine current version. Please check setup.py file."

check_prereq twine
check_prereq keyring

echo -e "------- Building version ${version} -------\n"
python setup.py sdist bdist_wheel >/dev/null


if [[ "$1" != "-p" ]]; then
    testing=1
    repo="https://test.pypi.org/legacy/"
    echo "Using test PyPi environment. Use 'mkpkg.sh -p' to upload to productive PyPi server."
else
    repo="https://upload.pypi.org/legacy/"
    echo "Uploading to productive PyPi server"
fi

echo -e "\nShould I upload the package to ${repo}? [Y/n]."
read yn
if [ "$yn" != "n" ]; then
    python -m twine upload --repository-url ${repo} dist/* || die "Not able to upload tp ${repo}"

    echo "Now test-install your package using:"
    echo
    [[ $testing ]] && export arg=" -i https://test.pypi.org/simple" || export arg=""
    echo "pip install${arg} --no-deps gdaps"
    echo "pipenv install${arg} gdaps"
    echo
fi

