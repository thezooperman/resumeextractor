# /usr/bin/env python

import errno
import json
import os
import pathlib
import random
import string
from io import StringIO

import plac
import spacy
from bs4 import BeautifulSoup
from spacy.util import compounding, minibatch

from fileop import FileOperation, walk_dir

BASE_DIR = pathlib.Path.cwd()
MODEL_PATH = BASE_DIR / 'model'
printable = set(string.printable)
ONLY_DIGITS = set(string.digits)

blacklisted_punctuation = {"'", '\\', '"'}


def strip_html(content):
    soup = BeautifulSoup(content, features='lxml')
    return soup.get_text().strip()


def clean_text(text):
    return ''.join([c for c in text if c in printable and c not in blacklisted_punctuation])


def test_read():
    for r in getResume():
        print(r)
        print('-' * 70)
        print('\n')


def clean_email():
    pass


def clean_phone(phone):
    '''
        Phone nos should be in 91xxxxxxxxxx format
    '''
    def _check_length(text):
        if not text:
            raise ValueError(errno.EINVAL, os.strerror(errno.EINVAL), text)
        assert (len(text) >= 10), 'Phone numbers must be 10 digits at least'
        # return last 10 digits, if length > 10
        text = ''.join(c for c in text if c.isdigit())
        if len(text) >= 10:
            text = text[-10:]
        return text

    if not phone:
        return None

    # remove extra space if present
    phone = ''.join(c for c in phone.split())
    #''.join(c for c in phone if c.isdigit())

    tokenizer = None
    # check if phone has multiple nos
    if ';' in phone:
        tokenizer = phone.split(';')
    elif '/' in phone:
        tokenizer = phone.split('/')
    prepend = '91'

    # check if phone has 10 or more characters
    if tokenizer:
        i = 0
        while i < len(tokenizer):
            tokenizer[i] = prepend + _check_length(tokenizer[i])
            i += 1
    else:
        phone = prepend + _check_length(phone)

    return tokenizer if tokenizer else phone


def convert_dataturks_to_spacy(dataturks_JSON_FilePath):
    try:
        training_data = []
        # lines = []
        with open(dataturks_JSON_FilePath, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                text = clean_text(strip_html(data['content']))
                entities = []
                for annotation in data['annotation']:
                    # only a single point in text annotation.
                    point = annotation['points'][0]
                    labels = annotation['label']
                    # handle both list of labels or a single label.
                    if not isinstance(labels, list):
                        labels = [labels]

                    for label in labels:
                        # dataturks indices are both inclusive [start, end] but spacy is not [start, end)
                        entities.append(
                            (point['start'], point['end'] + 1, label))
                training_data.append((text, {"entities": entities}))
        return training_data
    except Exception as e:
        print("Unable to process " + dataturks_JSON_FilePath +
              "\n" + "error = " + str(e))
    return None


def getResume():
    for f in walk_dir():
        try:
            fileOp = FileOperation(f)
            sb = StringIO()
            suffix = f.split('.')[1].lower()
            if suffix == 'docx':
                sb.write(''.join(clean_text(line)
                                 for line in fileOp.read_docx()))
            elif suffix == 'pdf':
                s = ''.join(clean_text(strip_html(_))
                            for _ in fileOp.read_pdf())
                sb.write(' '.join(_ for _ in s.split()))
            if len(sb.getvalue()) > 0:
                yield sb.getvalue()
            sb.close()
            del sb
            del fileOp
        except Exception as ex:
            print(f'ERROR: {ex}')


def run_model(model):
    print('Running against the trained model')
    nlp = spacy.load(model)  # load existing spaCy model
    print("Loaded model '%s'" % model)
    print()
    # pathlib.Path('/home/aritraghosh/MyWorkspace/resumeextractor/test_data/')):
    for resume in getResume():
        doc = nlp(resume)
        if len(doc.ents) > 0:
            print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
            print()


def convert_brat_to_spacy(brat_directory='/home/aritraghosh/Downloads/brat-v1.3_Crunchy_Frog/data/resumes'):
    try:
        train_data = []
        target_dir = pathlib.Path(brat_directory)
        ann_files = sorted(target_dir.glob('*.ann'))
        text_files = sorted(target_dir.glob('*.txt'))
        for ann, text in zip(ann_files, text_files):
            with open(target_dir / text, 'r', encoding='utf-8') as fp:
                content = fp.read()
            with open(target_dir / ann, 'r', encoding='utf-8') as fp:
                labels = []
                for line in fp:
                    splitted_line = line.split()
                    # start pos, end pos, label name
                    labels.append(
                        (int(splitted_line[2]), int(splitted_line[3]), splitted_line[1].replace("_", " ")))
            train_data.append((content, {"entities": labels}))
        return train_data
    except Exception as ex:
        print(f'Error: {ex}')
    return None


@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    output_dir=("Optional output directory", "option", "o", pathlib.Path),
    n_iter=("Number of training iterations", "option", "n", int),
    train_test=("Train(True - default) or Test(False) model",
                "option", "t", str),
)
def main(model=None, output_dir=None, n_iter=100, train_test="True"):
    """Load the model, set up the pipeline and train the entity recognizer."""
    if train_test == "False":
        run_model(model)
    else:
        if model is not None:
            nlp = spacy.load(model)  # load existing spaCy model
            print("Loaded model '%s'" % model)
        else:
            nlp = spacy.blank("en")  # create blank Language class
            print("Created blank 'en' model")

        # create the built-in pipeline components and add them to the pipeline
        # nlp.create_pipe works for built-ins that are registered with spaCy
        if "ner" not in nlp.pipe_names:
            ner = nlp.create_pipe("ner")
            nlp.add_pipe(ner, last=True)
        # otherwise, get it so we can add labels
        else:
            ner = nlp.get_pipe("ner")
        train_data = convert_brat_to_spacy()
        train_data.extend(convert_dataturks_to_spacy(
            BASE_DIR / 'train_data' / 'traindata.json'))
        # add labels
        for _, annotations in train_data:
            for ent in annotations.get("entities"):
                ner.add_label(ent[2])

        if model is None:
            optimizer = nlp.begin_training()
        else:
            # Note that 'begin_training' initializes the models, so it'll zero out
            # existing entity types.
            optimizer = nlp.entity.create_optimizer()

        # get names of other pipes to disable them during training
        other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
        with nlp.disable_pipes(*other_pipes):  # only train NER
            # reset and initialize the weights randomly – but only if we're
            # training a new model
            if model is None:
                nlp.begin_training()
            for _ in range(n_iter):
                random.shuffle(train_data)
                losses = {}
                # batch up the examples using spaCy's minibatch
                batches = minibatch(
                    train_data, size=compounding(4.0, 32.0, 1.001))
                for batch in batches:
                    texts, annotations = zip(*batch)
                    nlp.update(
                        texts,  # batch of texts
                        annotations,  # batch of annotations,
                        sgd=optimizer,
                        drop=0.50,  # dropout - make it harder to memorise data
                        losses=losses,
                    )
                print("Losses", losses)

        # test the trained model
        test_data = []
        test_data = convert_dataturks_to_spacy(
            BASE_DIR / 'test_data' / 'testdata.json')
        print('\nTesting on Test Data')
        for text, _ in test_data:
            doc = nlp(text)
            print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
        # print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])
        print('\nTesting on Train Data')
        # save model to output directory
        if output_dir is not None:
            output_dir = BASE_DIR / output_dir
            if not output_dir.exists():
                output_dir.mkdir()
            nlp.to_disk(output_dir)
            print("Saved model to", output_dir)

            # test the saved model
            print("Loading from", output_dir)
            nlp2 = spacy.load(output_dir)
            for text, _ in train_data:
                doc = nlp2(text)
                print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
                # print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])


if __name__ == '__main__':
    # plac.call(main)
    # test_read()
    # convert_brat_to_spacy()
    print(clean_phone('+91-888-440-483/09988 048821'))
