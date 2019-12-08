import setuptools

with open('README.md', 'rt') as f:
    ld = f.read()


setuptools.setup(
    name="FiniteConsole",
    version="1.0.2",
    license='MIT',
    author="Cyrille Kossyguine",
    author_email="lambda_man@outlook.fr",
    description="A way to simplify development of CLI applications",
    long_description=ld,
    long_description_content_type="text/markdown",
    url='https://github.com/cyrillelamal/FiniteConsole',
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True,
)
