try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

setup(name="Logbot",
      version="dev",
      packages=find_packages(),
      namespace_packages=['logbot'],
      include_package_data=True,
      author='Gavin McQuillan',
      author_email='gavin.mcquillan@gmail.com',
      description='Prototype Twisted Logbot',
      long_description='',
      zip_safe=False,
      platforms='any',
      license='MIT',
      url='https://github.com/urbanairship/logbot',
      classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Education',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Operating System :: Unix',
        ],

      entry_points={
        'console_scripts': [
            'logbot=logot.logbot:main',
            ],
        },
      )

