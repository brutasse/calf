from setuptools import find_packages, setup

with open('requirements.in') as reqs:
    install_requires = [line for line in reqs.read().split('\n') if (
        line and not line.startswith('--'))
    ]

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='calf',
    version='1.0',
    author='Bruno Renié',
    author_email='brutasse@gmail.com',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    url='https://github.com/brutasse/calf',
    license='BSD',
    long_description=long_description,
    install_requires=install_requires,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: System :: Logging',
    ),
    entry_points={'console_scripts': 'calf=calf.cli:main'},
    test_suite='tests',
    zip_safe=False,
)
