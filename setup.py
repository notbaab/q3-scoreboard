from setuptools import setup, find_packages

requires = [
    "Flask",
    "Flask-SQLAlchemy",
]

setup(name="q3_scoreboard",
      version='0.1',
      python_requires='>3.4.0',
      author="ET",
      packages=find_packages(),
      install_requires=requires,
      entry_points="""
      [console_scripts]
      q3-initdb=q3_scoreboard.models:init_db
      """,
      )
