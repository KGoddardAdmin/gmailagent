from setuptools import setup, find_packages

setup(
    name="gmail-mcp-server",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "mcp",
        "google-auth",
        "google-auth-oauthlib",
        "google-auth-httplib2", 
        "google-api-python-client",
        "python-dotenv",
        "pydantic",
        "httpx",
    ],
    entry_points={
        "console_scripts": [
            "gmail-mcp=gmail_mcp.server:main",
        ],
    },
)