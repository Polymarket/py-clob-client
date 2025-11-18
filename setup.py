import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py_clob_client",
    version="0.29.0",
    author="Polymarket Engineering",
    author_email="engineering@polymarket.com",
    maintainer="Polymarket Engineering",
    maintainer_email="engineering@polymarket.com",
    description="Python client for the Polymarket CLOB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Polymarket/py-clob-client",
    install_requires=[
        "eth-account>=0.13.0",
        "eth-utils>=4.1.1",
        "poly_eip712_structs>=0.0.1",
        "py-order-utils>=0.3.2",
        "python-dotenv",
        "py-builder-signing-sdk>=0.0.2",
        "httpx[http2]>=0.27.0",
    ],
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
