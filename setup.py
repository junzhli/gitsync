import gitsync

import setuptools

install_requires = [
    'gitdb2==2.0.5',
    'GitPython==2.1.11',
    'smmap2==2.0.5'
]

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gitsync",
    version=gitsync.__version__,
    author=gitsync.__author__,
    author_email="junzhli@gmail.com",
    description="A tiny sync tool integrated with Git system helps developers back up config and setting.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/junzhli/gitsync",
    packages=setuptools.find_packages(),
    python_requires='>=3',
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'gitsync=gitsync.__main__:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)