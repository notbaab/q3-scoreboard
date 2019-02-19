from setuptools import setup, find_packages

requires = [
    "flask",
    "Flask-SQLAlchemy",
]

setup(name="q3score",
      version='0.1',
      python_requires='>3.4.0',
      author="ET",
      packages=find_packages(),
      install_requires=requires,
      entry_points="""
      [console_scripts]
      q3-initdb=quake_scoreboard.models:init_db
      """,
      )
