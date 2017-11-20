from setuptools import setup

def build():
  setup(
    name = "sickdb",
    version = "0.0.1",
    author = "Brian Abelson",
    author_email = "brian@kickstarer.com",
    description = "Music analysis, standardization, and de-duplication.",
    license = "MIT",
    keywords = "DJ",
    url = "https://github.com/abelsonlive/sickdb",
    packages = ['sickdb'],
    install_requires = ['pytaglib', 'requests'],
    entry_points={
      'console_scripts': [
          'sickdb-analysis = sickdb.song:run',
          'sickdb-update = sickdb.box:run'
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