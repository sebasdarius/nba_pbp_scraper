from distutils.core import setup
setup(
  name = 'nba_pbp_scraper',
  packages = ['nba_pbp_scraper'],
  version = '0.1',
  license='MIT',
  description = 'Scrapes nba play by play data from basketball-reference.com',
  author = 'Jean Sebastien Darius',
  author_email = 'sebasdarius@gmail.com',
  url = 'https://github.com/sebasdarius/nba_pbp_scraper',
  download_url = 'https://github.com/sebasdarius/nba_pbp_scraper/archive/v_01.tar.gz',
  keywords = ['NBA', 'Play By Play', 'basketball-reference'],
  install_requires=[            # I get to this in a second
          'validators',
          'beautifulsoup4',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
