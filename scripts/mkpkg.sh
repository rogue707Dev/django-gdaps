#!/usr/bin/env bash

die() {
    # die  with amessage
    echo "ERROR:  $1"
    exit 1
}

if [ -d "dist/" ]; then
    die "Please delete the dist/ directory before proceeding."
fi

version=$(grep "version=" setup.py| cut -d '"' -f2)
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

python -m twine upload --repository-url ${repo} dist/* || die "Not able to upload tp ${repo}"

if [[ $testing ]]; then
    echo "Now test-install your package using this code:"
    echo
    echo "python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps gdaps"
fi

