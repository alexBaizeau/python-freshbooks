from setuptools import find_packages, setup

setup(
    name="python-freshbooks",
    author_email="alexandre.baizeau@gmail.com",
    license="MIT License",
    version="0.7.0",
    packages=find_packages(),
    install_requires=[
        "authlib",
    ],
    description="Python wrapper for the FreshBooks API",
    url="https://github.com/alexbaizeau/python-freshbooks",
)
