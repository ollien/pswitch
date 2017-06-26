from setuptools import setup

setup(
    name="pswitch",
    version="1.0",
    author="ollien",
    author_email="nick@ollien.com",
    url="https://github.com/ollien/pswitch",
    python_requires=">=3.0",
    packages=["pswitch"],
    entry_points={
        "console_scripts": [
            "pswitch=pswitch.__main__:main"
        ]
    }
)
