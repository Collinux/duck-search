#!/usr/bin/python
#
# Open the first result from DuckDuckGo.com given a search string as an argument
# (Separate from duck-search.py)
#
# Copyright (c) 2017 Collin Guarino
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This project is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with project.  If not, see <http://www.gnu.org/licenses/>.
import sys
import urllib2
import webbrowser
import BeautifulSoup
from urlparse import urlparse

def main():
    # Get the search string from the argument
    if len(sys.argv) == 1:
        print "A search string is required as an arguent to run duck-search"
        return
    sys.argv = sys.argv[1:]
    search_string = str(''.join(str(arg)+"+" for arg in sys.argv))
    search_string = search_string[:len(search_string)-1] # Remove last '+'

    # Parse duckduckgo and open the first page in the default browser
    url = 'https://duckduckgo.com/lite/?q=' + search_string 
    results = get_results(get_page(url))
    webbrowser.open(results[0]['link'])


def get_page(url):
    """
    Requests the HTML string from a page.

    Args:
        url: String pointing to the web page

    Returns:
        String if the server responds with 200 [SUCCESS], else None object.

    """
    page = urllib2.urlopen(url)
    page_code = page.getcode()
    # print "Server response [%s]" % str(page_code)
    if page_code == 200:
        return page.read()
    print "Error for url %, code %s" % (url, str(page_code))
    return None


def get_results(string):
    """
    Get the results list from the query

    Args:
        string: Full HTML string

    Returns:
        Dictionary with keys 'title', 'description', 'link'

    """
    # Get table rows containing the results
    soup = BeautifulSoup.BeautifulSoup(string)
    table = soup.findAll('table')[2]
    rows = table.findAll('tr')
    valid_rows = []
    for row in rows:
        if len(row) < 5:
            continue
        row = str(row)

        # Go through inner html for all text
        if 'result-link' in row:
            # Title section
            row = row[row.index('link">') + 6: row.index('</a>')]
            valid_rows.append(format_row(row))
        elif 'result-snippet' in row:
            # Description section
            row = row[row.index('snippet">') + 9: row.rindex('</td>')]
            valid_rows.append(format_row(row))
        elif 'link-text' in row:
            # Link section
            row = row[row.index('text">') + 6: row.index('</span>')]
            if 'http' not in row:
                row = 'http://' + row
            valid_rows.append(row)
        else:
            continue

    # Break the table rows into chunks of three, separating each row info
    counter = 0
    row_data = {}  # Looping structure below adds keys "title", "description", and "link"
    results = []
    for row in valid_rows:
        if counter == 0:
            row_data['title'] = row.title()
            counter += 1
        elif counter == 1:
            row_data['description'] = row
            counter += 1
        elif counter == 2:
            row_data['link'] = row
            results.append(row_data)

            # Reset all other vars
            counter = 0
            row_data = {}
    results = byteify(results)
    return results[0:5]

def byteify(input):
    """
    Conversion from unicode values to byte/string

    Args:
        input: String list

    Returns:
        Dictionary with unicode elements

    """
    if isinstance(input, dict):
        return dict([(byteify(key), byteify(value)) for key, value in input.iteritems()])
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input


def format_row(row):
    """
    Custom format for rows from the search result

    Args:
        row: String raw from html

    Returns:
        tring formatted for display

    """
    row = row.replace('<b>', '').replace('</b>', '').replace('\n', '').replace(
        '\t', '').replace('&amp;', '&').replace('&quot;', '"').replace('&nbsp;', '')
    return row.decode('UTF-8').strip()  # todo: UTF-8 decoding is not working

main()
