#!/usr/bin/python
#
# DuckDuckGo search with a terminal interface.
#
# Copyright (c) 2015  Collin Guarino
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
import curses
import urllib2
import webbrowser
import BeautifulSoup
import logging as log
from urlparse import urlparse


def search():
    # Setup debugging
    log.basicConfig(filename='ducksearch.log', level=log.DEBUG)

    # Load content
    search_string = ''
    for arg in sys.argv:
        search_string += arg + ' '
    search_for = build_url(search_string)
    page = get_page_html(search_for)
    results = get_results(page)
    if results is None:
        print "Cannot connect to DuckDuckGo."
        return

    # Configure window and screen
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    screen.keypad(1)

    count = 1
    screen.addstr('\n\n')
    for row in results:
        # Row Count
        screen.addstr('  %s.  ' % (str(count)))

        # URL
        parsed_uri = urlparse(row['link'])
        url = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)
        url = url[url.index('://') + 3:]
        space_string = ''
        section_length = 20
        if len(url) < section_length:
            space_string += ' ' * (section_length - len(url))
        screen.addstr('%s%s  ' % (url, space_string), curses.COLOR_CYAN)

        # Title
        screen.addstr('%s\n' % (row['title']), curses.COLOR_RED | curses.A_BOLD)

        # Description
        screen.addstr('%s\n\n\n' % row['description'], curses.COLOR_BLUE | curses.A_NORMAL)

        count += 1

    # Get keyboard input for commands/shortcuts
    screen.addstr('Enter a number to open the webpage:  ')
    running = True
    while running:
        char = screen.getkey()
        if char == 'q' or char == curses.KEY_CANCEL:
            running = False
        elif char.isdigit():  # todo: validity check 1-5  # todo: fix index bug. 0 index should open 1
            url = results[int(char)]['link']
            webbrowser.open(url)
    curses.endwin()


def row_formatting(row):
    """
    Custom format for rows from the search result

    Args:
        row: String raw from html

    Returns:
        String formatted for display

    """
    row = row.replace('<b>', '').replace('</b>', '').replace('\n', '').replace(
        '\t', '').replace('&amp;', '&').replace('&quot;', '"').replace('&nbsp;', '')
    return row.decode('UTF-8').strip()  # todo: UTF-8 decoding is not working


def get_results(string):
    """
    Get the results list from the query

    Args:
        string: Full HTML string

    Returns:
        Dictionary with keys "" # TODO

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
            valid_rows.append(row_formatting(row))
            # log.debug(row)
        elif 'result-snippet' in row:
            # Description section
            row = row[row.index('snippet">') + 9: row.rindex('</td>')]
            valid_rows.append(row_formatting(row))
            # log.debug(row)
        elif 'link-text' in row:
            # Link section
            row = row[row.index('text">') + 6: row.index('</span>')]
            if 'http' not in row:
                row = 'http://' + row
            valid_rows.append(row)
            # log.debug(row)
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


def get_page_html(url):
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


def build_url(args):
    """
    Attaches base URL for database site to query options.

    Args:
        args: String to search for

    Returns:
        Quest URL for a specific page

    """
    return 'https://duckduckgo.com/lite/?q=' + args.replace(' ', '+')


search()