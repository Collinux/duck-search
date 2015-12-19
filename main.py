import curses
import sys
import urllib2
import BeautifulSoup


# sys.stdout.write("\x1b]2;{0}\x07".format('DuckDuckGo Search'))  # Change terminal title
#
# # Standard curses configuration
# screen = curses.initscr()
# curses.noecho()
# curses.cbreak()
# screen.keypad(1)
#
# height = 80
# width = 80
# begin_x = 1
# begin_y = 1
# window = curses.newwin(height, width, begin_y, begin_x)
#
#
# def quit():
#     curses.endwin()
#
#
# screen.addstr("Pretty text\n", curses.COLOR_WHITE)
#
# input = screen.getch()
# if input == 'q':
#     quit()



def get_results(string):
    """
    Get the results list from the query

    Args:
        string: Full HTML string

    Returns:
        Dictionary with keys "" # TODO

    """
    # string = string[string.index('<tbody>'):string.index('</tbody>')]
    # print string

    soup = BeautifulSoup.BeautifulSoup(string)
    rows = soup.findAll('tr')
    valid_rows = []
    for row in rows:
        if len(row.text) > 0 and 'Next Page' not in row.text and row.text != '&nbsp;&nbsp;' and row.text != '&nbsp;':
            row = row.text.replace('&nbsp;', '')
            print row
            valid_rows.append(row)

    # Break the table rows into chunks of three, separating each row info
    counter = 0
    row_data = {}
    row_mass = []
    for row in valid_rows:
        if counter == 0:
            row_data['title'] = row[row.index('.')+1:]
            counter += 1
        elif counter == 1:
            row_data['description'] = row
            counter += 1
        elif counter == 2:
            row_data['link'] = row
            row_mass.append(row_data)

            # Reset all other vars
            counter = 0
            row_data = {}
    print str(byteify(row_mass))


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


search_for = build_url('python curses library')
page = get_page_html(search_for)
results = get_results(page)  # todo: check for NONE object
