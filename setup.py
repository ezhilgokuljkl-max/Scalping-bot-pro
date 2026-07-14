from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="scalping-bot",
    version="1.0.0",
    author="Trading Bot Developer",
    description="Production-ready scalping trading bot with TradingView integration and broker APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ezhilgokulabc-ship-it/Scalping-bot",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.12",
    entry_points={
        "console_scripts": [
            "scalping-bot=scalping_bot.cli:main",
        ],
    },
)
