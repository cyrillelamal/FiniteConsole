import setuptools

with open('README.md', 'rt') as f:
    long_description = f.read()


setuptools.setup(
    name="FiniteConsole",
    version="0.0.1",
    author="cyrillelamal",
    author_email="cyrillekossyguine@gmail.com",
    description="A way to simplify development of CLI applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
