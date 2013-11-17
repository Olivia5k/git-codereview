from distutils.core import setup

setup(
    name='git-eyeballs',
    version='0.0.1',
    url='https://github.com/thiderman/git-eyeballs',
    author='Lowe Thiderman',
    author_email='lowe.thiderman@gmail.com',
    description=('Code review for git, stored in the repository'),
    license='MIT',
    packages=['eyeballs'],
    scripts=[
        'bin/git-eyeballs'
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
    ],
)
