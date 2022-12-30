import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py_clob_client",
    version="0.1.4",
    author="Polymarket Engineering",
    author_email="engineering@polymarket.com",
    maintainer="Polymarket Engineering",
    maintainer_email="engineering@polymarket.com",
    description="Python client for the Polymarket CLOB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Polymarket/py-clob-client",
    install_requires=["python-dotenv", "py-order-utils>=0.1.1"],
    project_urls={
        "Bug Tracker": "https://github.com/Polymarket/py-clob-client/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires=">=3.9.10",
)
