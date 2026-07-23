from setuptools import setup, find_packages


setup(
    name="pylightlib",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[],
    extras_require={
        "test": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ],
        "qt": [
            "PyQt5",
        ],
        "textual": [
            "textual>=0.41.0",
        ],
    },
    python_requires=">=3.10",
)
