#!/usr/bin/env bash

python setup.py sdist bdist_wheel

if [ "$1" != "-p" ]; then
    repo="https://test.pypi.org/legacy/"
    echo "Uploading to test PyPi server repository. Use '-p' switch to upload to productive PyPi server"
else
    repo="https://pypi.org/legacy/"
    echo "uploading productive PyPi server"
fi

python -m twine upload --repository-url ${repo} dist/*

echo "Now test install your package using this code:"
echo
echo "python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps gdaps"


