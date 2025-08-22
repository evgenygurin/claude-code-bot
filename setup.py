from setuptools import setup, find_packages

setup(
    name="claude_code_bot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "anthropic",
        "pydantic>=2.0.0",
        "asyncio",
        "aiofiles",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "pytest-mock",
            "black",
            "isort",
            "flake8",
            "mypy",
            "types-aiofiles",
        ],
    },
    python_requires=">=3.12",
)

