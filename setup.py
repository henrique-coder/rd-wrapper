from setuptools import setup, find_packages
from pathlib import Path


setup(
    name='rd-wrapper',
    version='0.0.8',
    description='A simple and easy-to-use Python wrapper for Real-Debrid API (https://api.real-debrid.com)',
    long_description=Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    url='https://github.com/Henrique-Coder/rd-wrapper',
    author='Henrique-Coder',
    author_email='hjyz6rqyb@mozmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4',
        'fake-useragent',
        'httpx'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    python_requires='>=3.8'
)
