#!/usr/bin/python
# -*- coding: utf-8 -*
import re
import shutil

__author__ = "gisly"


from lxml import etree
import os
import codecs


def create_parent_tier_from_annotation_concatenation(filename, new_filename,
                                                     parent_tier, tier_to_concatenate,
                                                     new_tier_name, end_delimiter = '.'):
    srcTree = etree.parse(filename)
    parent_tier_element = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                parent_tier + '"]')[0]
    tier_to_concatenate_element = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                tier_to_concatenate + '"]')[0]
    new_tier_element = etree.SubElement(srcTree.getroot(), 'TIER', DEFAULT_LOCALE = 'ru',
                                       LINGUISTIC_TYPE_REF = parent_tier_element.attrib['LINGUISTIC_TYPE_REF'],
                                       TIER_ID = new_tier_name)

    for alignable_annotation in srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                   parent_tier + '"]/ANNOTATION/'
                                              'ALIGNABLE_ANNOTATION'):
        new_tier_element_annotation = etree.SubElement(new_tier_element, 'ANNOTATION')
        new_tier_element_alignable_annotation = \
            etree.SubElement(new_tier_element_annotation, 'ALIGNABLE_ANNOTATION',
            ANNOTATION_ID = new_tier_name + "_" + alignable_annotation.attrib['ANNOTATION_ID'],
            TIME_SLOT_REF1 = alignable_annotation.attrib['TIME_SLOT_REF1'],
            TIME_SLOT_REF2 = alignable_annotation.attrib['TIME_SLOT_REF2'])
        new_tier_annotation_value = etree.SubElement(new_tier_element_alignable_annotation,
                                                     'ANNOTATION_VALUE')
        new_tier_annotation_value.text = \
            get_concatenation(tier_to_concatenate_element, alignable_annotation.attrib['ANNOTATION_ID']) + end_delimiter

    all_tiers = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER')
    for tier in all_tiers:
        if tier.attrib.get('PARENT_REF') == parent_tier:
            tier.attrib['PARENT_REF'] = new_tier_name
            for annotation in tier.xpath('ANNOTATION/REF_ANNOTATION'):
                annotation.attrib['ANNOTATION_REF'] = new_tier_name + "_" + annotation.attrib['ANNOTATION_REF']


    srcTree.write(new_filename)

def create_child_tier_from_annotation_concatenation(filename, new_filename,
                                                    parent_tier, tier_to_concatenate, new_tier_name):
    srcTree = etree.parse(filename)
    tier_to_concatenate_element = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                tier_to_concatenate + '"]')[0]
    new_tier_element = etree.SubElement(srcTree.getroot(), 'TIER', DEFAULT_LOCALE = 'ru',
                                       LINGUISTIC_TYPE_REF = tier_to_concatenate_element.attrib['LINGUISTIC_TYPE_REF'],
                                       TIER_ID = new_tier_name)

    for parent_annotation in srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                   parent_tier + '"]/ANNOTATION/'
                                              'REF_ANNOTATION'):
        new_tier_element_annotation = etree.SubElement(new_tier_element, 'ANNOTATION')
        new_tier_element_ref_annotation = \
            etree.SubElement(new_tier_element_annotation, 'REF_ANNOTATION',
            ANNOTATION_ID = new_tier_name + '_' + parent_annotation.attrib['ANNOTATION_ID'],
            ANNOTATION_REF = parent_annotation.attrib['ANNOTATION_ID'])
        new_tier_annotation_value = etree.SubElement(new_tier_element_ref_annotation,
                                                     'ANNOTATION_VALUE')
        new_tier_annotation_value.text = get_concatenation(tier_to_concatenate_element,
                                                           parent_annotation.attrib['ANNOTATION_ID'],
                                                           '')
    srcTree.write(new_filename)


def create_child_gloss_tier_from_annotation_concatenation(filename,
                                                          new_filename,
                                                          parent_tier,
                                                          tier_to_concatenate_parent,
                                                          tier_to_concatenate, new_tier_name):
    srcTree = etree.parse(filename)
    tier_to_concatenate_element = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                tier_to_concatenate + '"]')[0]
    tier_to_concatenate_parent_element = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                       tier_to_concatenate_parent + '"]')[0]
    new_tier_element = etree.SubElement(srcTree.getroot(), 'TIER', DEFAULT_LOCALE = 'ru',
                                       LINGUISTIC_TYPE_REF = tier_to_concatenate_element.attrib['LINGUISTIC_TYPE_REF'],
                                       TIER_ID = new_tier_name)

    for parent_annotation in srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                   parent_tier + '"]/ANNOTATION/'
                                              'REF_ANNOTATION'):
        new_tier_element_annotation = etree.SubElement(new_tier_element, 'ANNOTATION')
        new_tier_element_ref_annotation = \
            etree.SubElement(new_tier_element_annotation, 'REF_ANNOTATION',
            ANNOTATION_ID = new_tier_name + '_' + parent_annotation.attrib['ANNOTATION_ID'],
            ANNOTATION_REF = parent_annotation.attrib['ANNOTATION_ID'])
        new_tier_annotation_value = etree.SubElement(new_tier_element_ref_annotation,
                                                     'ANNOTATION_VALUE')
        new_tier_annotation_value.text = get_child_concatenation(tier_to_concatenate_parent_element,
                                                                 tier_to_concatenate_element,
                                                           parent_annotation.attrib['ANNOTATION_ID'],
                                                           '')
    srcTree.write(new_filename)

def convert_plain_file(filename, new_filename, word_tier_name,
                       morphemes_tier_name, glosses_tier_name, parent_name):
    srcTree = etree.parse(filename)
    morphemes_tier_element = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                        morphemes_tier_name + '"]')[0]
    glosses_tier_element = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                         glosses_tier_name + '"]')[0]

    new_word_tier_element = etree.SubElement(srcTree.getroot(), 'TIER', DEFAULT_LOCALE='ru',
                                        LINGUISTIC_TYPE_REF=morphemes_tier_element.attrib['LINGUISTIC_TYPE_REF'],
                                        TIER_ID=word_tier_name,
                                        PARENT_REF=parent_name)
    new_morpheme_tier_element = etree.SubElement(srcTree.getroot(), 'TIER', DEFAULT_LOCALE='ru',
                                        LINGUISTIC_TYPE_REF=morphemes_tier_element.attrib['LINGUISTIC_TYPE_REF'],
                                        TIER_ID=morphemes_tier_name + "Concat",
                                        PARENT_REF=word_tier_name)
    new_gl_tier_element = etree.SubElement(srcTree.getroot(), 'TIER', DEFAULT_LOCALE='ru',
                                                 LINGUISTIC_TYPE_REF=morphemes_tier_element.attrib['LINGUISTIC_TYPE_REF'],
                                                 TIER_ID=glosses_tier_name + "Concat",
                                                 PARENT_REF=word_tier_name)
    for parent_annotation in srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                                      parent_name + '"]/ANNOTATION/'
                                              'ALIGNABLE_ANNOTATION'):
        annotation_id = parent_annotation.attrib['ANNOTATION_ID']
        morphemes = morphemes_tier_element.xpath('ANNOTATION/REF_ANNOTATION'
                                                              '[@ANNOTATION_REF="' +
                                                                      annotation_id + '"]/ANNOTATION_VALUE/text()')[0]
        words = morphemes.strip().split(" ")
        glosses = glosses_tier_element.xpath('ANNOTATION/REF_ANNOTATION'
                                              '[@ANNOTATION_REF="' +
                                              annotation_id + '"]/ANNOTATION_VALUE/text()')[0]
        glosses_parts = glosses.strip().split(" ")
        if len(glosses_parts) != len(words):

            raise Exception("len(glosses) != len(words)")


        previous_annotation_id = None
        for word_index, word in enumerate(words):
            new_tier_element_annotation = etree.SubElement(new_word_tier_element, 'ANNOTATION')
            word_annotation_id = word_tier_name + '_' + parent_annotation.attrib['ANNOTATION_ID'] \
                                 + "_" + str(word_index)
            new_tier_element_ref_annotation = \
                etree.SubElement(new_tier_element_annotation, 'REF_ANNOTATION',
                                 ANNOTATION_ID=word_annotation_id,
                                 ANNOTATION_REF=parent_annotation.attrib['ANNOTATION_ID'])
            if previous_annotation_id:
                new_tier_element_ref_annotation.attrib['PREVIOUS_ANNOTATION'] = previous_annotation_id
            new_tier_annotation_value = etree.SubElement(new_tier_element_ref_annotation,
                                                         'ANNOTATION_VALUE')
            word_cleared = re.sub('[\-\.\=]', '', word)
            new_tier_annotation_value.text = word_cleared
            previous_annotation_id = word_annotation_id

            new_morpheme_element_annotation = etree.SubElement(new_morpheme_tier_element, 'ANNOTATION')
            morpheme_annotation_id = morphemes_tier_name + '_' + parent_annotation.attrib['ANNOTATION_ID'] \
                                 + "_" + str(word_index)
            new_morpheme_element_ref_annotation = \
                etree.SubElement(new_morpheme_element_annotation, 'REF_ANNOTATION',
                                 ANNOTATION_ID=morpheme_annotation_id,
                                 ANNOTATION_REF=word_annotation_id)

            new_morpheme_element_ref_annotation_value = etree.SubElement(new_morpheme_element_ref_annotation,
                                                         'ANNOTATION_VALUE')
            new_morpheme_element_ref_annotation_value.text = word

            new_gloss_element_annotation = etree.SubElement(new_gl_tier_element, 'ANNOTATION')
            gloss_annotation_id = glosses_tier_name + '_' + parent_annotation.attrib['ANNOTATION_ID'] \
                                     + "_" + str(word_index)
            new_gloss_element_ref_annotation = \
                etree.SubElement(new_gloss_element_annotation, 'REF_ANNOTATION',
                                 ANNOTATION_ID=gloss_annotation_id,
                                 ANNOTATION_REF=word_annotation_id)

            new_gloss_element_ref_annotation_value = etree.SubElement(new_gloss_element_ref_annotation,
                                                                         'ANNOTATION_VALUE')
            new_gloss_element_ref_annotation_value.text = glosses_parts[word_index]


    srcTree.write(new_filename)


def copy_main_tier_to_child(filename, new_filename, main_tier, tier_model, new_tier, new_tier_parent):
    srcTree = etree.parse(filename)
    main_tier_element = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                      main_tier + '"]')[0]
    tier_model_element = srcTree.xpath('/ANNOTATION_DOCUMENT/TIER[@TIER_ID="' +
                                      tier_model + '"]')[0]

    new_tier_element = etree.SubElement(srcTree.getroot(), 'TIER', DEFAULT_LOCALE='ru',
                                        LINGUISTIC_TYPE_REF=tier_model_element.attrib['LINGUISTIC_TYPE_REF'],
                                        TIER_ID=new_tier,
                                        PARENT_REF=new_tier_parent)
    for alignable_annotation in main_tier_element.xpath('ANNOTATION/'
                                              'ALIGNABLE_ANNOTATION'):
        new_tier_element_annotation = etree.SubElement(new_tier_element, 'ANNOTATION')
        new_tier_element_ref_annotation = \
            etree.SubElement(new_tier_element_annotation, 'REF_ANNOTATION',
            ANNOTATION_REF = new_tier_parent + '_' + alignable_annotation.attrib['ANNOTATION_ID'],
            ANNOTATION_ID = new_tier + '_' + alignable_annotation.attrib['ANNOTATION_ID'])
        new_tier_annotation_value = etree.SubElement(new_tier_element_ref_annotation,
                                                     'ANNOTATION_VALUE')
        new_tier_annotation_value.text = \
            alignable_annotation.getchildren()[0].text

    srcTree.write(new_filename)

def get_child_concatenation(tier_to_concatenate_parent_element, tier_to_concatenate_element, annotation_id,
                            delimiter=' '):
    concatenated_values = ''
    for annotation in tier_to_concatenate_parent_element.xpath('ANNOTATION/REF_ANNOTATION'
                                                              '[@ANNOTATION_REF="' +
                                                                      annotation_id + '"]'):
        curAnnotationValue = annotation.xpath('ANNOTATION_VALUE/text()')[0]

        """concatenated_values += '' + get_concatenation(tier_to_concatenate_element, annotation.attrib['ANNOTATION_ID'],
                                                 '-')"""
        if curAnnotationValue.startswith('-'):
            delim = '-'
        elif curAnnotationValue.startswith('='):
            delim = '-'
        else:
            delim = ' '
        concatenated_values += delim + get_concatenation(tier_to_concatenate_element, annotation.attrib['ANNOTATION_ID'],
                                                         '')
    return re.sub('\-+', '-', concatenated_values.strip('-').strip())



def get_concatenation(tier_to_concatenate_element, annotation_id, delimiter=' '):
    concatenated_values = ''
    for annotation_value in tier_to_concatenate_element.xpath('ANNOTATION/REF_ANNOTATION'
                                              '[@ANNOTATION_REF="' +
                                                annotation_id + '"]/ANNOTATION_VALUE/text()'):
        concatenated_values += delimiter + annotation_value
    return concatenated_values.strip()

def prepare_file(filename, output_folder, language_tier_name):
    new_filename = os.path.join(output_folder, os.path.basename(filename))
    create_parent_tier_from_annotation_concatenation(filename, new_filename, language_tier_name, "fonWord", "sentFon")
    create_child_tier_from_annotation_concatenation(new_filename, new_filename,
                                                                   "fonWord", "fon", "fonConcat")
    create_child_gloss_tier_from_annotation_concatenation(new_filename,new_filename,
                                                                         "fonWord", "fon", "gl", "glConcat")
    copy_main_tier_to_child(new_filename, new_filename,
                                           language_tier_name, "rus", language_tier_name + "Cyr", "sentFon")
    return new_filename

def preprocess_folder(folder, output_folder, meta_folder, language_tier_name = "ev"):
    with codecs.open(os.path.join(meta_folder, 'meta.csv'), 'w', 'utf-8') as fout:
        fout.write('filename\r\n')
        for base_filename in os.listdir(folder):
            filename = os.path.join(folder, base_filename)
            if os.path.isfile(filename) and filename.lower().endswith('.eaf'):
                print('starting to process: %s' % filename)
                try:
                    new_filename = prepare_file(filename, output_folder, language_tier_name)
                    fout.write(os.path.splitext(os.path.basename(new_filename))[0] + '\n')
                    print('processed: %s'  % filename)
                except Exception as e:
                    print(e)
                    print('error occurred when processing: %s' % filename)



def copy_media_for_file(filename, folder_media):
    media_file_uri = get_media_file_uri(filename)
    if not media_file_uri:
        print('No media for %s' % filename)
        return
    if not os.path.exists(media_file_uri):
        print('File does not exist for %s: %s' % (media_file_uri, filename))
        return
    if media_file_uri.endswith('.avi'):
        print('AVI file for %s: %s' % (media_file_uri, filename))
        return
    base_filename = os.path.basename(media_file_uri)
    target_filename = os.path.join(folder_media, base_filename)
    shutil.copy(media_file_uri, target_filename)

def get_media_file_uri(filename):
    srcTree = etree.parse(filename)
    main_media_elements = srcTree.xpath('/ANNOTATION_DOCUMENT/HEADER/MEDIA_DESCRIPTOR'
                                        '[@MIME_TYPE="audio/x-wav"]')
    if not main_media_elements:
        main_media_elements = srcTree.xpath('/ANNOTATION_DOCUMENT/HEADER/MEDIA_DESCRIPTOR')
    if not main_media_elements:
        return None
    return main_media_elements[0].attrib['MEDIA_URL'].split('file:///')[-1]

def copy_media(folder_eaf, folder_media):
    for filename in os.listdir(folder_eaf):
        full_eaf_filename = os.path.join(folder_eaf, filename)
        copy_media_for_file(full_eaf_filename, folder_media)
        print('Moved file for %s' % full_eaf_filename)



"""create_parent_tier_from_annotation_concatenation(,
                                          "ev", "fonWord", "evFon")

create_child_tier_from_annotation_concatenation("D://ForElan//ForSIL_CORPUS//"
                                          "evenki_corpus//eaf//2007_Chirinda_Eldogir_Valentina_FSk9_test.eaf_new.eaf",
                                          "fonWord", "fon", "fonConcat")

create_child_gloss_tier_from_annotation_concatenation("D://ForElan//ForSIL_CORPUS//"
                                          "evenki_corpus//eaf//2007_Chirinda_Eldogir_Valentina_FSk9_test.eaf_new.eaf_new.eaf",
                                          "fonWord", "fon", "gl", "glConcat")"""
"""
preprocess_folder("D://CompLing/CorpusUtils/tsakonian_corpus_platform/corpus/evenki//test//",
                  "D://CompLing/CorpusUtils/tsakonian_corpus_platform/corpus/evenki/eaf",
                  "D://CompLing/CorpusUtils/tsakonian_corpus_platform/corpus/evenki")"""

"""preprocess_folder("D://CompLing/CorpusUtils/tsakonian_corpus_platform/corpus/ket//test//",
                  "D://CompLing/CorpusUtils/tsakonian_corpus_platform/corpus/ket/eaf",
                  "D://CompLing/CorpusUtils/tsakonian_corpus_platform/corpus/ket",
                  "ket")"""

"""create_child_gloss_tier_from_annotation_concatenation("D://ForElan//OldMethod//1998_Sovrechka_Saygotina_Vera_LR//"
                                                "1998_Sovrechka_Saygotina_Vera_LR_transliterated_new.eaf",
"D://ForElan//OldMethod//1998_Sovrechka_Saygotina_Vera_LR//"
                                                "1998_Sovrechka_Saygotina_Vera_LR_transliterated_new2.eaf",
                                          "fonConcat", "fon", "gl", "glConcat");"""

"""
copy_media("D://CompLing/CorpusUtils/tsakonian_corpus_platform/corpus/evenki/eaf",
           "D://CompLing/CorpusUtils/tsakonian_corpus_platform/corpus/evenki/media")"""

print(get_media_file_uri("D://CompLing/CorpusUtils/tsakonian_corpus_platform/"
                         "corpus/evenki/eaf/2007_Chirinda_Eldogir_Valentina_LR1.eaf_new.eaf"))