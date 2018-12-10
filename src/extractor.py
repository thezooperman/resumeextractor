# /usr/bin/env python

import errno
import os
import pathlib
import PyPDF2

from docx import Document

BASE_DIR = pathlib.Path.cwd()
INPUT_PATH = BASE_DIR / 'input'
OUTPUT_PATH = BASE_DIR / 'output'
ARCHIVE_PATH = BASE_DIR / 'archive'


class FileOperation:
    '''
    Utility to read, write files.
    Also has basic validations.
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

    def __move_processed_to_archive(self):
        archive_path = pathlib.Path(ARCHIVE_PATH)
        try:
            if not archive_path.exists():
                archive_path.mkdir(parents=True, exist_ok=True)
            os.rename(self.__construct_file_path(),
                      archive_path / self.file_name)
        finally:
            del archive_path

    def __write_to_output(self):
        output_path = pathlib.Path(OUTPUT_PATH)
        try:
            if not output_path.exists():
                output_path.mkdir(parents=True, exist_ok=True)
            os.rename(self.__construct_file_path(),
                      output_path / self.file_name)
        finally:
            del output_path

    def read_docx(self):
        ''' Read a Doc/Docx file and return contents as generator object'''
        construct_file_path = self.__construct_file_path()
        try:
            dox = Document(construct_file_path)
            if not dox:
                raise ValueError(f'{self.file_name}',
                                 errno.EBADFD, os.strerror(errno.EBADFD))
            for para in dox.paragraphs:
                yield para.text.strip()
            self.__move_processed_to_archive()
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
            for page in range(pdf_reader.numPages):
                content = pdf_reader.getPage(page)
                yield content.extractText().strip()
            self.__move_processed_to_archive()
        finally:
            del pdf_reader
            fp.close()
            del fp
            del construct_file_path


if __name__ == '__main__':
    print('Read DocX')
    print('-' * 20)
    dummyFile = 'demo.docx'
    read_file = FileOperation(dummyFile)
    print(read_file.file_name)
    [print(p) for p in read_file.read_docx()]
    del read_file
    print('Read PDF')
    print('-' * 20)
    dummyFile = 'combinedminutes.pdf'
    read_file = FileOperation(dummyFile)
    print(read_file.file_name)
    for idx, p in enumerate(read_file.read_pdf()):
        if idx == 0:
            print(p)
