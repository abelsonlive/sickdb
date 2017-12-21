from setuptools import setup


def build():
    setup(
        name="sickdb",
        version="0.0.1",
        author="Brian Abelson",
        author_email="brian@kickstarer.com",
        description="Music analysis, standardization, and de-duplication.",
        license="MIT",
        keywords="DJ",
        url="https://github.com/abelsonlive/sickdb",
        packages=['sickdb', 'sickdb.config'],
        install_requires=['pytaglib', 'requests'],
        entry_points={
            'console_scripts': [
                'sickdb = sickdb.__main__:main',
                'sickdb-update = sickdb.__main__:run_update',
                'sickdb-dedupe = sickdb.__main__:run_dedupe',
                'sickdb-to-itunes = sickdb.__main__:run_to_itunes'
            ]
        },
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Topic :: Communications :: Email",
            "License :: OSI Approved :: MIT License",
        ]
    )

if __name__ == '__main__':
    build()
