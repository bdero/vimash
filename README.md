vimash
======

Vimash is a **vi**deo **ma**sher; it slices random clips from videos taken from
a set of YouTube search results and glues them together, producing high quality
rediculousness.

Installation
------------
```sh
# Clone the repository
git clone https://github.com/bdero/vimash
cd vimash

# Install the dependencies
pip2 install -r requirements.txt

# Copy the sample configuration and follow the instructions within to generate
#   a YouTube Data API key
cp config.example.yml config.yml
cat config.yml

# View the help message
python2 generator.py --help
```

License
-------
Copyright (C) 2015  Brandon DeRosier

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
[GNU General Public License](LICENSE.md) for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
