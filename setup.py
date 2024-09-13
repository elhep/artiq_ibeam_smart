from setuptools import find_packages, setup

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="artiq_ibeam_smart",
    install_requires=required,
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "artiq_ibeam_smart= artiq_ibeam_smart.artiq_ibeam_smart:main",
        ],
    },
)
