from setuptools import setup


setup(
    name="zosftpmock",
    version='0.1',
    packages=['zosftpmock'],
    author="realitix",
    author_email="realitix@gmail.com",
    description="Zos FTP Mock",
    long_description="Allow to test FTP client again z/OS FTP server",
    install_requires=['pyftpdlib'],
    include_package_data=True,
    url="http://github.com/realitix/zos-ftpmock",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.5",
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    license="Apache 2.0",
    entry_points={
        'console_scripts': [
            'zosftp = zosftpmock.main:main'
        ]
    }
)
