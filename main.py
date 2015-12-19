import curses
import urllib2
import BeautifulSoup


def start():
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

    if results is None:
        print "Cannot connect to DuckDuckGo."
        return
    for row in results:
        screen.addstr(row['title']+'\n', curses.COLOR_WHITE)

    # Get keyboard input for commands/shortcuts
    running = True
    while running:
        char = screen.getch()
        if char == ord('q') or char == curses.KEY_CANCEL:
            running = False
        # todo: HJKL move commands
    curses.endwin()


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
    rows = soup.findAll('tr')
    valid_rows = []
    for row in rows:
        if len(row.text) > 0 and 'Next Page' not in row.text and row.text != '&nbsp;&nbsp;' and row.text != '&nbsp;':
            valid_rows.append(row.text.replace('&nbsp;', ''))

    # Break the table rows into chunks of three, separating each row info
    counter = 0
    row_data = {}  # Looping structure below adds keys "title", "description", and "link"
    results = []
    for row in valid_rows:
        if counter == 0:
            row_data['title'] = row[row.index('.')+1:]  # Remove number from the title
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
    print results


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


def get_inner_html(input):
    """
    Mimics javascript's innerHTML function.

    If there are multiple links then return all values (comma separated)
    Example: <A HREF="http://website.html" NAME="center">WEB</A> - with "WEB" being the value

    Args:
        input: String of all characters

    Returns:
        String of HTML value in-between '> <'.

    """
    output = []
    for link in input.split('<A'):
        if '>' in link and '<' in link:
            link = link[link.index('>') + 1:link.rindex('<')]
            if len(link) > 0:
                output.append(link)
    return output


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
