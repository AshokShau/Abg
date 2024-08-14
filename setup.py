from setuptools import setup, find_packages

VERSION = '2.3.9.beta.01'
DESCRIPTION = 'add-on for Pyrogram || add-on for Pyrogram || Telegram bot helpers || Easy botting'
with open("README.md", encoding="utf8") as readme:
    long_description = readme.read()


setup(
    name="Abg",
    version=VERSION,
    author="Abishnoi (Ashok Bishnoi)",
    author_email="<abishnoi69@outlook.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['python-dotenv~=1.0.1', 'cachetools~=5.3.3', 'pytz>=2024.1'],
    keywords="add-on bots telegram bot hydrogram pyrogram",
    url="https://github.com/Abishnoi69/Abg",
    download_url="https://github.com/Abishnoi69/Abg/releases/latest",
    license="MIT",
    classifiers=[
        "Development Status :: 2 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet",
        "Topic :: Communications",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    project_urls={
        "Tracker": "https://github.com/Abishnoi69/Abg/issues",
        "Community": "https://t.me/Abgpy",
        "Source": "https://github.com/Abishnoi69/Abg",
        "Documentation": "https://abg.abishnoi.me/",
    },
    python_requires=">=3.8",
)
