from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="gdaps",
    version="0.3.4",
    author="Christian González",
    # author_email="author@example.com",
    description="Generic Django Apps Plugin System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Documentation": "https://gdaps.readthedocs.io",
        "Source": "https://gitlab.com/nerdocs/gdaps",
        "Tracker": "https://gitlab.com/nerdocs/gdaps/issues",
    },
    install_requires=["django"],
    url="https://gitlab.com/nerdocs/gdaps",
    packages=find_packages(exclude=["contrib", "docs", "tests*"]),
    license="GPLv3",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python",
    ],
)
