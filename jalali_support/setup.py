from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

setup(
    name="jalali-support",
    version="0.1.0",
    description="Jalali (Persian) calendar support for Frappe / ERPNext",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Custom",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "frappe>=14.0.0",
    ],
    python_requires=">=3.10",
)
