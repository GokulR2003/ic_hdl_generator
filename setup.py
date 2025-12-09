from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ic-hdl-generator",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Generate Verilog/VHDL from IC metadata using templates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ic-hdl-generator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=[
        "jinja2>=3.0.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "ic-hdl-gen=src.hdl_generator:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": [
            "hdl_templates/**/*",
            "testbench_templates/**/*",
            "config/*",
        ],
    },
)
