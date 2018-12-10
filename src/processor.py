# /usr/bin/env python

import spacy
from fileop import FileOperation, walk_dir
from io import StringIO

nlp = spacy.load('en')


def test_nlp():
    file_name = 'Ayush Kush.pdf'
    file_op = FileOperation(file_name)
    sb = StringIO()
    sb.write(''.join([line.strip() for line in file_op.read_pdf()]))
    # print(sb.getvalue())
    doc = nlp(sb.getvalue())
    sb.close()
    # print(doc.ents)
    for t in doc.ents:
        print(t, t.label_)



if __name__ == '__main__':
    test_nlp()
