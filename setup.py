import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="electoral_system_analysis",
    version="0.0.9",
    author="Santiago Arranz Sanz",
    description="Repositorio que recoge diferentes elementos de sistemas electorales "
    "para su comparación, dentro de los marcos de la constitución española de 1978.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    url="https://github.com/santhiperbolico/analisis-de-sistemas-electorales",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    py_modules=["electoral_system_analysis"],
    package_dir={"": "src"},
    install_requires=["pandas"],
)
