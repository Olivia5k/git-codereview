from distutils.core import setup

setup(
    name='git-codereview',
    version='0.0.1',
    url='https://github.com/thiderman/git-codereview',
    author='Lowe Thiderman',
    author_email='lowe.thiderman@gmail.com',
    description=('Code review for git, stored in the repository'),
    license='MIT',
    packages=['codereview'],
    scripts=[
        'bin/git-codereview'
        'bin/git-cr'
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
    ],
)
