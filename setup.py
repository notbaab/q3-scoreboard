from setuptools import setup, find_packages

requires = [
    "Flask>=1.1.1",
    "Flask-SQLAlchemy>=2.4.1",
]

setup(name="q3_scoreboard",
      version='0.1',
      python_requires='>3.4.0',
      author="ET",
      packages=find_packages(),
      install_requires=requires,
      include_package_data=True,
      entry_points="""
      [console_scripts]
      q3-initdb=q3_scoreboard.models:init_db
      """,
      )
