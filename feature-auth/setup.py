from setuptools import setup, find_packages

setup(
    name="ff-codex-auth",
    version="0.1.0",
    description="Authentication service for FF Codex",
    author="FF Codex Team",
    author_email="dev@ffcodex.com",
    packages=find_packages(where="app"),
    package_dir={"": "app"},
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.95.0",
        "uvicorn>=0.21.0",
        "sqlalchemy>=2.0.0",
        "pydantic>=1.10.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.5",
        "python-dotenv>=0.21.0",
        "loguru>=0.6.0",
        "email-validator>=1.3.0",
        "python-dateutil>=2.8.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "httpx>=0.23.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
            "pylint>=2.17.0",
            "pytest-cov>=4.0.0",
        ],
        "postgres": ["asyncpg>=0.27.0"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    entry_points={
        "console_scripts": [
            "ff-codex-auth=main:app",
        ],
    },
)
