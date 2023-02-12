# markdown_it usage at https://markdown-it-py.readthedocs.io/en/latest/using.html
# CommonMark reference: https://commonmark.org/help/
from django import template
from django.template.defaultfilters import stringfilter
from markdown_it import MarkdownIt
register = template.Library()


@register.filter()
@stringfilter
def commonMark(value):
    '''Given a string in CommonMark, return it in HTML form.'''
    return MarkdownIt('commonmark').render(value)


if __name__ == "__main__":
    # a basic test
    testString = '# hello!'
    # print(testString)
    assert (commonMark(testString) == "<h1>hello!</h1>\n")
