import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="electoral_system_analysis",
    version="0.0.6",
    author="Santiago Arranz Sanz",
    description="Repositorio que recoge diferentes elementos de sistemas electorales "
    "para su comparación, dentro de los marcos de la constitución española de 1978.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.8",
    py_modules=["electoral_system_analysis"],
    package_dir={"": "src/electoral_system_analysis/"},
    install_requires=["pandas"],
)
