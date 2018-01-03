from setuptools import setup, find_packages


setup(
    name='mvc',
    version='0.1',
    description='MVC',
    license='Apache License (2.0)',
    author='Ibadulla Khan',
    packages=find_packages(),
    package_data={'mvc': ['db/migrations/migrate.cfg']},
)
