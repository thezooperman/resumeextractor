from google.cloud import language_v1 as language
from google.cloud.language_v1 import enums
from google.cloud.language_v1 import types
import six
from fileop import FileOperation
from io import StringIO


def entities_text(text):
    """Detects entities in the text."""
    client = language.LanguageServiceClient()

    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    # Instantiates a plain text document.
    document = types.Document(
        content=text,
        type=enums.Document.Type.HTML)

    # Detects entities in the document. You can also analyze HTML with:
    #   document.type == enums.Document.Type.HTML
    entities = client.analyze_entities(document).entities

    # entity types from enums.Entity.Type
    entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION',
                   'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER', 'DATE')

    for entity in entities:
        if entity_type[entity.type] in ('PERSON', 'DATE'):
            print('=' * 20)
            print(u'{:<16}: {}'.format('name', entity.name))
            print(u'{:<16}: {}'.format('type', entity_type[entity.type]))
            print(u'{:<16}: {}'.format('metadata', entity.metadata))
            print(u'{:<16}: {}'.format('salience', entity.salience))
            print(u'{:<16}: {}'.format('wikipedia_url',
                                       entity.metadata.get('wikipedia_url', '-')))


if __name__ == '__main__':
    # text = 'Ayush Kush software engineer. He wants '\
    #     'to apply in KPMG for a Data Scientist job in '\
    #     'December 2018 at Bangalore, Karnataka, India'
    # text = 'Ayush Kush Associate Business Analyst 3.8 years '\
    #     'of experiences in analytics. Possess comprehensive '\
    #     'knowledge of data science techniques (including data '\
    #     'modeling, data mining, machine learning).'
    # print(text)
    # entities_text(text)
    # FileOperation('Astajyoti Behera.docx')
    fileOp = FileOperation('Vaibhav Misra.pdf')
    sb = StringIO()
    sb.writelines('\n'.join(s.strip() for s in fileOp.read_pdf()))
    # print(sb.getvalue())
    entities_text(sb.getvalue())
    sb.close()
    del fileOp
    del sb
    del entities_text
