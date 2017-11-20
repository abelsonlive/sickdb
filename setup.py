from setuptools import setup

def build():
  setup(
    name = "sickdropbox",
    version = "0.0.1",
    author = "Brian Abelson",
    author_email = "brian@kickstarer.com",
    description = "ITunes library analysis, standardization, and de-duplication.",
    license = "MIT",
    keywords = "DJ",
    url = "https://github.com/abelsonlive/sickdropbox",
    packages = ['sickdropbox'],
    install_requires = ['pytaglib', 'requests'],
    entry_points={
      'console_scripts': [
          'sickdb-analysis = sickdropbox.song:run',
          'sickdb-update = sickdropbox.box:run'
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