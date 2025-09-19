#!/usr/bin/env python3
"""
SellerLegend Python SDK Setup
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sellerlegend-api",
    version="1.0.2",
    author="SellerLegend",
    author_email="support@sellerlegend.com",
    description="Official Python SDK for the SellerLegend API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sellerlegend/sellerlegend_api_py",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    keywords="sellerlegend api amazon seller ecommerce analytics sellercentral sp-api",
    project_urls={
        "Bug Reports": "https://github.com/sellerlegend/sellerlegend_api_py/issues",
        "Source": "https://github.com/sellerlegend/sellerlegend_api_py",
        "Documentation": "https://dashboard.sellerlegend.com/api-docs/index.html",
    },
)