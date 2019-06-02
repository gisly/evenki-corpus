from gen_wfms_with_repr import WordformGenerator
from gen_ready_wfms import MockMorphParser
import random
import copy
import numpy as np
import json


class WordSearchTree:
    """
    Binary search tree that can quickly choose a random word
    taking into account its frequency, given a random number
    between 0 and 1.
    For the sake of reducing search time, words whose probabilities
    differ by less than MIN_INTERVAL can be considered to have same
    probabilities.
    """
    MIN_INTERVAL = 1e-4

    def __init__(self, mid=0.5, pmin=0.0, pmax=1.0):
        self.hapax_cutoff = 0.5  # words right to this are considered to have equal probability
        self.hapaxes = []        # hapax legomena in the rightmost branch
        self.left = None
        self.right = None
        self.wfs = None
        self.pmin = pmin
        self.pmax = pmax
        self.mid = mid

    def add_word(self, wf, pmin, pmax):
        if pmax > self.hapax_cutoff:
            self.hapaxes.append(wf)
            if pmin < self.hapax_cutoff:
                self.add_word(wf, pmin, self.hapax_cutoff)
            return
        if pmin <= self.pmin and pmax >= self.pmax:
            self.wfs = [wf]
            # print(wf.wf, self.pmin, self.pmax)
            return
        elif pmin >= self.pmax or pmax <= self.pmin:
            return
        elif self.pmax - self.pmin < self.MIN_INTERVAL:
            if self.wfs is None:
                self.wfs = [wf]
            else:
                self.wfs.append(wf)
            return
        if pmin < self.mid:
            if self.left is None:
                self.left = WordSearchTree(mid=(self.pmin + self.mid) / 2,
                                           pmin=self.pmin,
                                           pmax=self.mid)
            self.left.add_word(wf, pmin, pmax)
        if pmax > self.mid:
            if self.right is None:
                self.right = WordSearchTree(mid=(self.mid + self.pmax) / 2,
                                            pmin=self.mid,
                                            pmax=self.pmax)
            self.right.add_word(wf, pmin, pmax)

    def find_word(self, p):
        # print('find_word', self.pmin, self.mid, self.pmax, p)
        if self.wfs is not None:
            return random.choice(self.wfs)
        elif p >= self.hapax_cutoff:
            if len(self.hapaxes) <= 1:
                p /= 2
                return self.find_word(p)
            iWf = random.randint(0, len(self.hapaxes) - 1)
            return self.hapaxes.pop(iWf)
        elif self.pmin <= p < self.mid:
            if self.left is None:
                return None
            return self.left.find_word(p)
        elif self.mid <= p <= self.pmax:
            if self.right is None:
                return None
            return self.right.find_word(p)


class Sentence:
    def __init__(self):
        self.text = ''
        self.words = []

    def __len__(self):
        return len(self.words)


class Punctuation:
    def __init__(self, text):
        self.wf = text
        self.wtype = 'punct'


class Text:
    """
    an object of this class generates meta and
    writes .json files for given sentence sequences
    """
    def __init__(self, sentences, length, author, title, numwords, i):
        self.sentences = sentences
        self.create_meta(length, author, title, numwords, i)

    def create_meta(self, length, author, title, numwords, i):
        self.meta = {}
        self.meta['author'] = author
        self.meta['title'] = title
        self.meta['year'] = random.randint(1960, 2017)
        self.meta['id'] = i
        self.meta['sentences'] = length
        self.meta['words'] = numwords

    def write_json(self):
        """
        writes corpus to .json file
        """
        f = open('test_output/'+str(self.meta['id'])+'.json', 'w', encoding='utf-8-sig')
        self.sentences = [x.__dict__ for x in self.sentences]
        f.write(json.dumps(self.__dict__, indent=1, ensure_ascii=False))
        f.close()
  
class CorpusGenerator:
    """
    object of this class, when created, generates corpus
    out of WordForm class objects and some random puctuation
    """
    def __init__(self, settings):
        self.settings = settings
        self.wfTree = None
        self.generate_sents()

    def create_full_wordforms(self):
        """
        returns wordforms with analyses
        """
        f = open('settings.json', 'r', encoding='utf-8')
        settings = json.loads(f.read())
        f.close()
        generator = WordformGenerator(settings)
        mp = MockMorphParser(settings, 30000)
        n = 0
        for wf in generator.wordforms:
            n += mp.add_analysis(wf)
        print(n / len(generator.wordforms))
        return generator.wordforms

    def final_sent(self, sent_arr):
        """
        returns an object of Sentence class
        """
        sent = Sentence()
        text = ''
        punct = np.random.choice([0, 1], len(sent_arr), p=[0.9, 0.1])
        offset = 0
        for i, item in enumerate(sent_arr):
            try: #delete frequency attribute
                delattr(item,'freq')
            except:
                pass
            dup_item = copy.deepcopy(item)
            dup_item.off_start = offset
            offset += len(dup_item.wf)
            dup_item.off_end = offset
            sent.words.append(dup_item.__dict__)
            text += dup_item.wf
            if punct[i] and i != len(sent_arr) - 1:
                punc_item = Punctuation(np.random.choice([';', ',', ':']))
                punc_item.off_start = offset
                offset += 1
                punc_item.off_end = offset
                sent.words.append(punc_item.__dict__)
                text += punc_item.wf
            if i != len(sent_arr) - 1:
                text += ' '
                offset += 1
            else:
                finalpunct = Punctuation(np.random.choice(['.', '!', '?'],
                                                          p=[0.7, 0.15, 0.15]))
                finalpunct.off_start = offset
                offset += 1
                finalpunct.off_end = offset
                text += finalpunct.wf
                sent.words.append(finalpunct.__dict__)
        text = text[0].upper() + text[1:]
        sent.text = text
        return sent

    def build_wf_cdf(self, wfms):
        """
        Build a search tree with the cumulative distribution
        function for the choice of wordforms, taking into account
        their frequencies.
        """
        # nWfs = self.settings['constants']['LENGTH_OF_CORPUS']
        nWfs = sum(wf.freq for wf in wfms)
        prevPoint = 0
        self.wfTree = WordSearchTree()
        for wf in wfms:
            wfFreq = wf.freq / nWfs
            self.wfTree.add_word(wf, prevPoint, prevPoint + wfFreq)
            prevPoint += wfFreq

    def pick_random_word(self):
        r = random.random()
        wf = None
        while wf is None:
            wf = self.wfTree.find_word(r)
        return wf
    
    def generate_sents(self):
        """
        Generates full corpus (list of objects of Sentence class),
        writing it to json files.
        """
        self.sentences = []
        wfms = self.create_full_wordforms()
        self.build_wf_cdf(wfms)
        # full_corp = len(full_list)
        nCorpusSize = self.settings['constants']['LENGTH_OF_CORPUS']
        mean = np.mean(np.log(self.settings['constants']['MEAN_SENT_LENGTH']))
        nGenerated = 0
        prevGenerated = 0
        textlength = random.randint(100,3000)
        textnum = 1
        while nGenerated < nCorpusSize:
            # print(nGenerated)
            length = int(np.round(np.random.lognormal(mean=mean)))
            while length > self.settings['constants']['MAX_SENT_LENGTH'] or length < 1:
                length = round(np.random.lognormal(mean=mean))
            sentence = [self.pick_random_word()
                        for _ in range(min([length, nCorpusSize - nGenerated]))]
            nGenerated += len(sentence)
            self.sentences.append(self.final_sent(sentence))
            if nGenerated >= nCorpusSize:
                textlength = len(self.sentences)
            if len(self.sentences) == textlength:
                author = [self.pick_random_word() for _ in range(2)]
                author = ' '.join([x.wf[0].upper()+x.wf[1:] for x in author])
                title = ' '.join([self.pick_random_word().wf 
                                  for _ in range(random.randint(1,5))])
                title = title[0].upper() + title[1:]
                wordsInText = nGenerated - prevGenerated
                text = Text(self.sentences, textlength, author, title, wordsInText, textnum)
                text.write_json()
                textlength = random.randint(100, 3000)
                textnum += 1
                prevGenerated = nGenerated
                self.sentences = []
            
        #print('mean sentence length:', np.sum([len(x) for x in self.sentences]) / len(self.sentences))


if __name__ == '__main__':
    f = open('settings.json', 'r', encoding='utf-8')
    settings = json.loads(f.read())
    f.close()
    gen = CorpusGenerator(settings)
    gen.generate_sents()
