# /usr/bin/env python

import errno
import re
import os
import pathlib
import zipfile
from xml.etree.cElementTree import XML

import fitz

BASE_DIR = pathlib.Path.cwd()
INPUT_PATH = BASE_DIR / 'input'
OUTPUT_PATH = BASE_DIR / 'output'
ARCHIVE_PATH = BASE_DIR / 'archive'
WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
PARA = WORD_NAMESPACE + 'p'
TEXT = WORD_NAMESPACE + 't'
TABLE = WORD_NAMESPACE + 'tbl'
ROW = WORD_NAMESPACE + 'tr'
CELL = WORD_NAMESPACE + 'tc'


class FileOperation(object):
    '''
    Utility to read, write files.
    Also has basic validations.
    TODO: 
        # Unit Testing
        # using spacy for NER
        # implement logging
    '''

    __slots__ = ('file_name', )

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

    def __is_valid_file(self, fp):
        if not fp:
            raise ValueError(f'{self.file_name}',
                             errno.EBADF, os.strerror(errno.EBADF))

    def __move_processed_to_archive(self):
        archive_path = pathlib.Path(ARCHIVE_PATH)
        try:
            if not archive_path.exists():
                archive_path.mkdir(parents=True, exist_ok=True)
            os.rename(self.__construct_file_path(),
                      archive_path / self.file_name)
        finally:
            del archive_path

    def __write_to_output(self, content):
        output_path = pathlib.Path(OUTPUT_PATH)
        try:
            if not output_path.exists():
                output_path.mkdir(parents=True, exist_ok=True)

        finally:
            del output_path

    def read_pdf(self):
        ''' Read a PDF file and return contents as generator object'''
        construct_file_path = self.__construct_file_path()
        try:
            pdf_reader = fitz.open(construct_file_path)
            self.__is_valid_file(pdf_reader)
            # print(f'PDF Pages: {pdf_reader.pageCount}')
            for page in range(pdf_reader.pageCount):
                yield ' '.join(_ for _ in pdf_reader.loadPage(page).getText('html').split())
            # self.__move_processed_to_archive()
        finally:
            del pdf_reader
            del construct_file_path

    def read_docx(self):
        """
        Take the path of a docx file as argument, return the text in unicode.
        """
        try:
            document = zipfile.ZipFile(self.__construct_file_path())
            xml_content = document.read('word/document.xml')
            tree = XML(xml_content)

            for paragraph in tree.getiterator(PARA):
                for node in paragraph.getiterator(TEXT):
                    if node.text:
                        yield ' '.join(_ for _ in node.text.split())
            # self.__move_processed_to_archive()
        finally:
            if document is not None:
                document.close()
                del document
            if tree is not None:
                tree.clear()
                del tree


def walk_dir(input_dir=None):
    '''Walk through an input(resumes) directory.
        If a directory is not provided, the 'input'
        folder is the default directory set
    '''
    if not input_dir:
        input_dir = INPUT_PATH
    # iterate through directory
    for elem in input_dir.iterdir():
        if elem.is_file():
            yield elem.name


if __name__ == '__main__':
    file_counter = 0
    for f in walk_dir():
        fileOp = FileOperation(f)
        hitFlag = False
        suffix = f.split('.')[1]
        if suffix in ('docx', 'doc'):
            hitFlag = True
            for i in fileOp.read_docx():
                pass
        elif suffix == 'pdf':
            hitFlag = True
            for obj in fileOp.read_pdf():
                pass
        file_counter += 1
        if hitFlag:
            print(f'{file_counter}. File: {f}')
