from setuptools import setup, find_packages

setup(
    name='SAS Programmers Toolkit(Development)',
    version='0.1',
    description='A JupyterHub distribution with SAS tools',
    url='https://github.com/tom-henrich/sptoolkit',
    author='Tom Henrich',
    author_email='tomhenrich.dev@gmail.com',
    license='',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'ruamel.yaml==0.15.*',
        'jinja2',
        'pluggy>0.7<1.0',
        'passlib',
        'backoff',
        'requests',
        'bcrypt',
        'jupyterhub-traefik-proxy==0.1.*'
    ],
    entry_points={
        'console_scripts': [
            'jhub-config = jhub.config:main',
        ],
    },
)
