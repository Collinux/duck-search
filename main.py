import curses
import urllib2
import BeautifulSoup
import logging as log

def start():
    # Setup debugging
    log.basicConfig(filename='ducksearch.log', level=log.DEBUG)

    # Configure window and screen
    screen = curses.initscr()
    height, width = screen.getmaxyx()
    begin_x = begin_y = 1
    window = curses.newwin(height, width, begin_y, begin_x)
    curses.noecho()
    curses.cbreak()
    screen.keypad(1)

    # Load content
    # todo: get input
    search_for = build_url('python curses library')
    page = get_page_html(search_for)
    results = get_results(page)

    log.debug(str(results))

    if results is None:
        print "Cannot connect to DuckDuckGo."
        return
    for row in results:
        continue
        #row = '%s\n%s\n%s\n-----------------------------------------' % (row['title'], row['description'], row['link'])
        #screen.addstr(row, curses.COLOR_WHITE)
        #screen.addstr(row['description']+'\n', curses.COLOR_WHITE)
        # screen.addstr(row['link']+'\n', curses.COLOR_WHITE)
        # screen.addstr('------------------------------------', curses.COLOR_BLUE)

    # Get keyboard input for commands/shortcuts
    running = True
    while running:
        char = screen.getch()
        if char == ord('q') or char == curses.KEY_CANCEL:
            running = False
        # todo: HJKL move commands
    curses.endwin()


def row_formatting(row):
    """
    Custom format for rows from the search result

    Args:
        row: String raw from html

    Returns:
        String formatted for display

    """
    return row.translate(None, '<b></b>\t\n&amp;&quot;').strip().title().decode('utf-8')


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
            row = row[row.index('link">')+6: row.index('</a>')]
            valid_rows.append(row_formatting(row))
            #log.debug(row)
        elif 'result-snippet' in row:
            # Description section
            row = row[row.index('snippet">')+9: row.rindex('</td>')]
            valid_rows.append(row_formatting(row))
            #log.debug(row)
        elif 'link-text' in row:
            # Link section
            row = row[row.index('text">')+6: row.index('</span>')]
            if 'http' not in row:
                row = 'http://' + row
            valid_rows.append(row)
            #log.debug(row)
        else:
            continue

    # Break the table rows into chunks of three, separating each row info
    counter = 0
    row_data = {}  # Looping structure below adds keys "title", "description", and "link"
    results = []
    for row in valid_rows:
        if counter == 0:
            row_data['title'] = row
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
    return results[0:4]


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


start()
