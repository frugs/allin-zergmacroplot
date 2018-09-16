import setuptools

VERSION = "0.0.15"

setuptools.setup(
    name="zergmacroplot",
    packages=setuptools.find_packages(),
    package_data={"zergmacroplot": ["templates/*", "static/styles/*"]},
    version=VERSION,
    description="SC2 Replay Analyser which visualises a player's Zerg Macro Mechanics",
    author="Hugo Wainwright",
    author_email="wainwrighthugo@gmail.com",
    url="https://github.com/frugs/allin-zergmacroplot",
    keywords=["sc2", "replay", "sc2reader"],
    classifiers=[],
    install_requires=[
        "techlabreactor", "requests-toolbelt>=0.8.0", "pyrebase", "flask", "google-cloud-datastore"
    ],
)
