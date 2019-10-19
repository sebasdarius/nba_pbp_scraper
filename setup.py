from distutils.core import setup
setup(
  name = 'nba_pbp_scraper',
  packages = ['nba_pbp_scraper'],
  version = '1.0',
  license='MIT',
  description = 'Scrapes nba play by play data from basketball-reference.com',
  author = 'Jean Sebastien Darius',
  author_email = 'sebasdarius@gmail.com',
  url = 'https://github.com/sebasdarius/nba_pbp_scraper',
  download_url = 'https://github.com/sebasdarius/nba_pbp_scraper/archive/1.0.tar.gz',
  keywords = ['NBA', 'Play By Play', 'basketball-reference'],
  install_requires=[
          'pandas',
          'bs4',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7'
  ],
)
