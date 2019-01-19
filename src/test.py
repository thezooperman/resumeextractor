try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML
import string
import zipfile
from io import StringIO

from bs4 import BeautifulSoup

from fileop import FileOperation

"""
Module that extract text from MS XML Word document (.docx).
(Inspired by python-docx <https://github.com/mikemaccana/python-docx>)
"""

WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
PARA = WORD_NAMESPACE + 'p'
TEXT = WORD_NAMESPACE + 't'
printable = set(string.printable)
blacklisted_punctuation = {"'", '\\', '"'}


def clean_text(text):
    return ''.join([c for c in text if c in printable and c not in blacklisted_punctuation])


def strip_html(content):
    soup = BeautifulSoup(content, features='lxml')
    return soup.get_text().strip()


def get_docx_text(path):
    """
    Take the path of a docx file as argument, return the text in unicode.
    """
    document = zipfile.ZipFile(path)
    xml_content = document.read('word/document.xml')
    document.close()
    tree = XML(xml_content)

    paragraphs = []
    for paragraph in tree.getiterator(PARA):
        texts = [node.text
                 for node in paragraph.getiterator(TEXT)
                 if node.text]
        if texts:
            paragraphs.append(''.join(texts))

    # return '\n'.join(paragraphs)
    return ' '.join(clean_text(_) for _ in ' '.join(paragraphs).split())


def get_pdf_text(path):
    fileOp = FileOperation(path)
    paragraphs = []
    for line in fileOp.read_pdf():
        paragraphs.append(line)
    string = StringIO()
    s = ''.join(clean_text(strip_html(_))
                for _ in fileOp.read_pdf())
    string.write(' '.join(_ for _ in s.split()))
    print(string.getvalue().strip())


if __name__ == '__main__':
    path = 'input/Raghu Nanden.docx'
    print(get_docx_text(path))
    # get_pdf_text(path)
