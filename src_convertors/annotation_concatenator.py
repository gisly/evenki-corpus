#!/usr/bin/python
# -*- coding: utf-8 -*
import re

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

def prepare_file(filename, output_folder):
    new_filename = os.path.join(output_folder, os.path.basename(filename))
    create_parent_tier_from_annotation_concatenation(filename, new_filename, "ev", "fonWord", "sentFon")
    create_child_tier_from_annotation_concatenation(new_filename, new_filename,
                                                                   "fonWord", "fon", "fonConcat")
    create_child_gloss_tier_from_annotation_concatenation(new_filename,new_filename,
                                                                         "fonWord", "fon", "gl", "glConcat")
    copy_main_tier_to_child(new_filename, new_filename,
                                           "ev", "rus", "evCyr", "sentFon")
    return new_filename

def preprocess_folder(folder, output_folder, meta_folder):
    with codecs.open(os.path.join(meta_folder, 'meta.csv'), 'w', 'utf-8') as fout:
        fout.write('filename\r\n')
        for base_filename in os.listdir(folder):
            filename = os.path.join(folder, base_filename)
            if os.path.isfile(filename) and filename.lower().endswith('.eaf'):
                #print('starting to process: %s' % filename)
                try:
                    new_filename = prepare_file(filename, output_folder)
                    fout.write(os.path.splitext(os.path.basename(new_filename))[0] + '\n')
                    #print('processed: %s'  % filename)
                except Exception as e:
                    print(e)
                    print('error occurred when processing: %s' % filename)






"""create_parent_tier_from_annotation_concatenation(,
                                          "ev", "fonWord", "evFon")

create_child_tier_from_annotation_concatenation("D://ForElan//ForSIL_CORPUS//"
                                          "evenki_corpus//eaf//2007_Chirinda_Eldogir_Valentina_FSk9_test.eaf_new.eaf",
                                          "fonWord", "fon", "fonConcat")

create_child_gloss_tier_from_annotation_concatenation("D://ForElan//ForSIL_CORPUS//"
                                          "evenki_corpus//eaf//2007_Chirinda_Eldogir_Valentina_FSk9_test.eaf_new.eaf_new.eaf",
                                          "fonWord", "fon", "gl", "glConcat")"""

preprocess_folder("D://CompLing/CorpusUtils/tsakonian_corpus_platform/corpus/evenki//test//",
                  "D://CompLing/CorpusUtils/tsakonian_corpus_platform/corpus/evenki/eaf",
                  "D://CompLing/CorpusUtils/tsakonian_corpus_platform/corpus/evenki")

"""create_child_gloss_tier_from_annotation_concatenation("D://ForElan//OldMethod//1998_Sovrechka_Saygotina_Vera_LR//"
                                                "1998_Sovrechka_Saygotina_Vera_LR_transliterated_new.eaf",
"D://ForElan//OldMethod//1998_Sovrechka_Saygotina_Vera_LR//"
                                                "1998_Sovrechka_Saygotina_Vera_LR_transliterated_new2.eaf",
                                          "fonConcat", "fon", "gl", "glConcat");"""