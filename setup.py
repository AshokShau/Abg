import os
from typing import Dict

from setuptools import setup, find_packages

base_path = os.path.abspath(os.path.dirname(__file__))

about: Dict = {}
with open(
        os.path.join(
            base_path,
            'Abg',
            '__version__.py',
        ), encoding='utf-8',
) as f:
    exec(f.read(), about)

DESCRIPTION = 'add-on for Pyrogram || add-on for Hydrogram || Telegram bot helpers || Easy botting'
with open("README.md", encoding="utf8") as readme:
    long_description = readme.read()

setup(
    name="Abg",
    version=about["__version__"],
    author="AshokShau (Ashok)",
    author_email="<abishnoi69@outlook.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[
        'python-dotenv',
        'cachetools',
        'pytz',
    ],
    extras_require={
        'hydrogram': [
            'hydrogram',
            'TgCrypto-pyrofork'
        ],
        'pyrofork': [
            'pyrofork'
            'TgCrypto-pyrofork'
        ],
        'dev': [
            'setuptools'
            'twine',
        ]
    },
    keywords="add-on bots telegram bot hydrogram pyrogram",
    url="https://github.com/AshokShau/Abg",
    download_url="https://github.com/AshokShau/Abg/releases/latest",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
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
        "Tracker": "https://github.com/AshokShau/Abg/issues",
        "Community": "https://t.me/Abgpy",
        "Source": "https://github.com/AshokShau/Abg",
        "Documentation": "https://abg.abishnoi.me/",
    },
    python_requires=">=3.8",
)
