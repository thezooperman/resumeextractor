# /usr/bin/env python

import spacy
from fileop import FileOperation, walk_dir
from io import StringIO
from bs4 import BeautifulSoup
from spacy.matcher import Matcher

nlp = spacy.load('en')


def strip_html(content):
    soup = BeautifulSoup(content, features='lxml')
    return soup.get_text()


def test_nlp():
    file_name = 'Sakshi Seth.pdf'
    file_op = FileOperation(file_name)
    sb = StringIO()
    sb.write(' '.join([line for line in file_op.read_pdf()]))
    matcher = Matcher(nlp.vocab)
    pattern_phone = [{'SHAPE': 'ddddd'}, {
        'ORTH': '-', 'OP': '?'}, {'SHAPE': 'ddddd'}]
    pattern_phone_with_country_code = [{'ORTH': '+', 'OP': '?'},
                                       {'SHAPE': 'dd', 'OP': '?'},
                                       {'ORTH': '-', 'OP': '?'},
                                       {'SHAPE': 'ddddd'},
                                       {'ORTH': '-', 'OP': '?'},
                                       {'SHAPE': 'ddddd'}]
    patterns = []
    patterns.append(pattern_phone)
    patterns.append(pattern_phone_with_country_code)
    matcher.add('PHONE_NUMBER', None, pattern_phone_with_country_code)
#     print(sb.getvalue())
#     print(strip_html(sb.getvalue()))
    # doc = nlp(strip_html(sb.getvalue()))
    doc = nlp('Call me at +918884404883 or +91-8884404883 or 8884404883 or 88844-04883 or +91-88844-04883')
    sb.close()
#     print(doc.ents)
    # for t in doc.ents:
    #     print(t, t.label_)
    print([t.text for t in doc])
    matches = matcher(doc)

    for match_id, start, end in matches:
        span = doc[start:end]
        print(span.text)


if __name__ == '__main__':
    test_nlp()
