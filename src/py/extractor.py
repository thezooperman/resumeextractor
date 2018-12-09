# /usr/bin/env python

import errno
import os
import pathlib

from docx import Document

BASE_DIR = pathlib.Path.cwd()
INPUT_PATH = BASE_DIR / 'input'


class ReadFile:
    '''
    TODO: 
        # Add code to read from excel
        # Add code to read from csv 
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
        construct_file_path = self.__construct_file_path()
        dox = Document(construct_file_path)
        for para in dox.paragraphs:
            yield para.text
        del dox
        del construct_file_path


if __name__ == '__main__':
    dummyFile = 'demo.docx'
    read_file = ReadFile(dummyFile)
    print(read_file.file_name)
    [print(p) for p in read_file.read_docx()]
