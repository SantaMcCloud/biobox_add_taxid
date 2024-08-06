from setuptools import setup

## install main application
desc = "utility script for adding taxid to a binning file in biobox format"
setup(
    name="biobox_add_taxid",
    description=desc,
    long_description=desc + "\n See README for more information.",
    author="Santino Faack",
    author_email="santino_faack@gmx.de",
    license="MIT license",
    url="https://github.com/SantaMcCloud/biobox_add_taxid",
    scripts=[
        "script/biobox_add_taxid.py"
    ],
)