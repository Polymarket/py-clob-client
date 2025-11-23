# A modern setup.py file often contains only dynamic logic (like reading files).
# Most static metadata should be moved to setup.cfg or pyproject.toml for best practices.

import setuptools

# Open and read the contents of the README file for the long description.
# Using 'with open' ensures the file handle is properly closed.
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# All static metadata has been moved to setup.cfg or pyproject.toml in a real-world scenario.
# Here, we keep it in setup.py but ensure clean formatting and specific version range.
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
        # Dependency version ranges are cleanly specified
        "eth-account>=0.13.0",
        "eth-utils>=4.1.1",
        "poly_eip712_structs>=0.0.1",
        "py-order-utils>=0.3.2",
        "python-dotenv",
        "py-builder-signing-sdk>=0.0.2",
        # Use extras for conditional dependencies like http2
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
    # Automatically find and include all packages in the directory
    packages=setuptools.find_packages(),
    # Set Python minimum version requirement (broadened from 3.9.10 to >=3.9 for standard practice)
    python_requires=">=3.9",
)
