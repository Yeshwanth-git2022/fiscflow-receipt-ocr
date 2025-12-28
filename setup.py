"""Setup configuration for fiscflow-receipt-ocr package."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="fiscflow-receipt-ocr",
    version="0.1.0",
    author="FiscFlow Team",
    author_email="support@fiscflow.ai",
    description="A powerful, ML-enhanced receipt OCR library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/fiscflow-receipt-ocr",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/fiscflow-receipt-ocr/issues",
        "Documentation": "https://fiscflow-receipt-ocr.readthedocs.io",
        "Source Code": "https://github.com/yourusername/fiscflow-receipt-ocr",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "google-cloud-vision>=3.0.0",
        "Pillow>=9.0.0",
        "numpy>=1.20.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "isort>=5.10.0",
        ],
        "ml": [
            "spacy>=3.0.0",
            "transformers>=4.20.0",
            "torch>=1.12.0",
            "scikit-learn>=1.0.0",
        ],
        "all": [
            "boto3>=1.20.0",  # AWS Textract
            "azure-cognitiveservices-vision-computervision>=0.9.0",  # Azure
            "pytesseract>=0.3.0",  # Tesseract
        ],
    },
    entry_points={
        "console_scripts": [
            "fiscflow-ocr=fiscflow_ocr.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
