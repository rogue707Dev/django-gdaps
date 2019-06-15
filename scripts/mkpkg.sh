#!/usr/bin/env bash

die() {
    # die  with amessage
    echo "ERROR:  $1"
    exit 1
}


#version=$(grep "version=" setup.py| cut -d '"' -f2)
version=$(grep "__version__" gdaps/__init__.py | cut -d '"' -f2)
[[ "$version" == "" ]] && die "Could not determine current version. Please check setup.py file."

python -m keyring >/dev/null || die "Please install keyring in this virtualenv."

echo -e "------- Building version ${version} -------\n"
python setup.py sdist bdist_wheel >/dev/null


if [[ "$1" != "-p" ]]; then
    testing=1
    repo="https://test.pypi.org/legacy/"
    echo "Using test PyPi environment. Use 'mkpkg.sh -p' to upload to productive PyPi server."
else
    repo="https://upload.pypi.org/legacy/"
    echo "Uploading productive PyPi server"
fi

echo -e "\nShould I upload the package to ${repo}? [Y/n]."
read yn
if [ "$yn" != "n" ]; then
    python -m twine upload --repository-url ${repo} dist/* || die "Not able to upload tp ${repo}"

    echo "Now test-install your package using this code:"
    echo
    [[ $testing ]] && export arg="-i https://test.pypi.org/simple" || export arg=""
    echo "pip install ${arg} --no-deps gdaps"

fi

