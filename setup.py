from setuptools import setup, find_packages

setup(
    name="rlangc",
    version="0.1.0",
    description="A general-purpose language blending Python readability, JavaScript expressiveness, and C familiarity",
    author="RLangC Contributors",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "rlangc=cli:main",
        ],
    },
)
