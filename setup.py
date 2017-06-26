from setuptools import setup

setup(
    name="pulse-switch",
    version="1.0",
    author="ollien",
    author_email="nick@ollien.com",
    url="https://github.com/ollien/pulseswitch",
    packages=["pulseswitch"],
    entry_points={
        "console_scripts": [
            "pswitch=pulseswitch.__main__:main"
        ]
    }
)
