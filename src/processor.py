# /usr/bin/env python

from fileop import FileOperation, walk_dir
from io import StringIO
from bs4 import BeautifulSoup
import spacy
import string
from spacy.matcher import Matcher

nlp = spacy.load('en')
printable = set(string.printable)

def strip_html(content):
    soup = BeautifulSoup(content, features='lxml')
    return soup.get_text()

def clean_text(text):
    return ''.join([c for c in text if c in printable])

def test_nlp():
    try:
        file_name = 'Sakshi Seth.pdf'
        file_op = FileOperation(file_name)
        sb = StringIO()
        sb.write(''.join([clean_text(strip_html(line)).strip() for line\
                                        in file_op.read_pdf()]))
        matcher = Matcher(nlp.vocab)
        pattern_phone = [{'SHAPE': 'ddddd'}, {'ORTH': '-', 'OP': '?'}, {'SHAPE': 'ddddd'}]
        matcher.add('PHONE_NUMBER', None, pattern_phone)
        cleaned_doc = nlp(sb.getvalue().strip())
        #print(cleaned_doc)
        matches = matcher(cleaned_doc)
        #for t in cleaned_doc.ents:
            #print(t, t.label_)
        for match_id, start, end in matches:
            print(doc[start:end].text)
    finally:
        if sb:
            sb.close()
    
def trainData():
    train_data = []
    '''
    for f in walk_dir():
        fileOp = FileOperation(f)
        sb = StringIO()
        suffix = f.split('.')[1]
        if suffix in ('docx', 'doc'):
            sb.write(''.join([clean_text(line).strip() for line\
                                        in fileOp.read_docx()]))
        elif suffix == 'pdf':
            hitFlag = True
            for obj in fileOp.read_pdf():
                pass
        print(sb.getvalue().strip())
        sb.close()
    '''
    file_name = 'Raghu Nanden.docx'
    file_op = FileOperation(file_name)
    for line in file_op.read_docx():
        print(line.strip())


if __name__ == '__main__':
    trainData()
    #test_nlp()

