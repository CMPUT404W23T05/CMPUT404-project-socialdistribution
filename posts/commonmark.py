# markdown_it usage at https://markdown-it-py.readthedocs.io/en/latest/using.html
# CommonMark reference: https://commonmark.org/help/
from markdown_it import MarkdownIt


def markToHTML(input):
    '''Given a string in CommonMark, return it in HTML form.'''
    return MarkdownIt('commonmark').render(input)


if __name__ == "__main__":
    testString = '# hello!'
    # print(testString)
    assert (markToHTML(testString) == "<h1>hello!</h1>\n")
