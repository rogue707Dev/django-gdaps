from setuptools import setup, find_packages

setup(
    name="gdaps",
    version="0.0.1",
    author="Christian González",
    # author_email="author@example.com",
    description="Generic Django Apps Plugin System",
    install_requires=["django"],
    url="https://gitlab.com/nerdocs/gdaps",
    packages=["gdaps"],
    license="GPLv3",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
)
