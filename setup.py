from setuptools import setup

setup(
    name='xport',
    packages=['xport'],
    long_description=__doc__,
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'flask_wtf',
        'python-dotenv',
    ],
    scripts=[
        'scripts/xport-config',
        'scripts/xport-run',
    ],
)
