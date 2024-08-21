from setuptools import setup, find_packages

## install main application
desc = "utility script for adding taxid to a binning file in biobox format"
setup(
    name="biobox_add_taxid",
    version='0.3',
    description=desc,
    long_description=desc + "\n See README for more information.",
    author="Santino Faack",
    author_email="santino_faack@gmx.de",
    license="MIT license",
    packages=find_packages(),
    url="https://github.com/SantaMcCloud/biobox_add_taxid",
    scripts=[
        "script/biobox_add_taxid.py"
    ],
)
