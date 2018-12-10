# /usr/bin/env python

import errno
import os
import pathlib
import PyPDF2

from docx import Document

BASE_DIR = pathlib.Path.cwd()
INPUT_PATH = BASE_DIR / 'input'


class ReadFile:
    '''
    TODO: 
        # Unit Testing
        # using spacy for NER
    '''

    def __init__(self, file_name=None):
        self.file_name = file_name

        def _file_validation():
            if file_name is None:
                raise ValueError(
                    f'FileName: {file_name}', errno.EINVAL, os.strerror(errno.EINVAL))
            relative_fp = self.__construct_file_path()
            if not relative_fp.exists():
                raise ValueError(
                    f'FileName: {file_name}', errno.ENOENT, os.strerror(errno.ENOENT))
            if not relative_fp.is_file() or relative_fp.is_dir():
                raise ValueError(
                    f'{file_name} is not a valid File or is a Directory')
            del relative_fp
        _file_validation()

    def __construct_file_path(self):
        return INPUT_PATH / self.file_name

    def read_docx(self):
        ''' Read a Doc/Docx file and return contents as generator object'''
        construct_file_path = self.__construct_file_path()
        try:
            dox = Document(construct_file_path)
            if not dox:
                raise ValueError(f'{self.file_name}',
                                 errno.EBADFD, os.strerror(errno.EBADFD))
            for para in dox.paragraphs:
                yield para.text
        finally:
            del dox
            del construct_file_path

    def read_pdf(self):
        ''' Read a PDF file and return contents as generator object'''
        construct_file_path = self.__construct_file_path()
        try:
            fp = open(construct_file_path, 'rb')
            pdf_reader = PyPDF2.PdfFileReader(fp)
            if not pdf_reader:
                raise ValueError(f'{self.file_name}',
                                 errno.EBADFD, os.strerror(errno.EBADFD))
            print(f'PDF Pages: {pdf_reader.numPages}')
            page = pdf_reader.getPage(1)
            yield page.extractText()
        finally:
            del pdf_reader
            fp.close()
            del fp
            del construct_file_path


if __name__ == '__main__':
    print('Read DocX')
    print('-' * 20)
    dummyFile = 'demo.docx'
    read_file = ReadFile(dummyFile)
    print(read_file.file_name)
    [print(p) for p in read_file.read_docx()]
    del read_file
    print('Read PDF')
    print('-' * 20)
    dummyFile = 'combinedminutes.pdf'
    read_file = ReadFile(dummyFile)
    print(read_file.file_name)
    [print(p) for p in read_file.read_pdf()]
