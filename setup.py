import setuptools


where = "src"
setuptools.setup(
    name="kepler-model-server",
    version="0.0.0",  # TODO: Update version
    python_requires="~=3.8",
    url="https://github.com/sustainable-computing-io/kepler-model-server",
    packages=setuptools.find_packages(where=where),
    package_dir={"": where},
)
