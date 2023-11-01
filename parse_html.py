# author:   sam tenka
# change:   2023-10-31
# create:   2023-10-31
# descrp:   Identify media items (url + caption) from html.
# to use:   To parse a string `my_html`, write:
#               `from parse_html import get_items   `
#               `bb = get_items(my_html)            `
#           Then each item in `bb` is a dictionary such as
#             {
#               'text'      : None,
#               'imageurl'  : 'https://...',
#               'imagecap'  : 'Figure 28.  A cow balancing...',
#               'videourl'  : None,
#               'videocap'  : None,
#               'audiourl'  : None,
#               'audiocap'  : None,
#             }
#           Sometimes media items will lack a caption.
#           OR, to verify parser: in same folder as `test-figures`, run
#               `python3 parse_html.py`
#           and make sure it prints `ALL OK!` instead of aborting with an error

import re
import tqdm

# The test file consists of a bunch of paragraphs separated by triple-newlines,
# some of which start with '---' and are comments, and the remainder of which
# should each contain a single "content item": prose, image, video, or audio:
TEST_FILE = 'test-figures'

#==============================================================================
#===  HTML REGEX HELPERS  =====================================================
#==============================================================================

chomp = lambda: '[ ]*'
maybe  = lambda s: '({:s})?'.format(s)

group = lambda label: lambda s: '(?P<{:s}>{:s})'.format(label, s)

until = lambda c: '[^{:s}]*'.format(c)

begtag = lambda tag: '<{:s}'.format(tag) + '( [^>]*)?>' + chomp()
endtag = lambda tag: '</{:s}>'.format(tag) + chomp()
parse_tag = lambda tag: lambda inner: (
        '<' + tag + settings() + inner + until('>') + '>' + chomp()
        )

settings = lambda: '( [-a-z]+(="[^"\n]*")?)*'
parse_setting = lambda lhs: lambda label: (
        ' {:s}="{:s}"'.format(lhs, group(label)(until('"')))
        )

to_next_tag = lambda: r'([^<\n]|<[^>]*>)*' # allows one layer of tag nesting

#==============================================================================
#===  REGEXES TO EXPORT  ======================================================
#==============================================================================

media_regex = lambda TAG: (''
    +begtag('figure')
    +parse_tag(TAG)(parse_setting('src')(TAG+'url'))
    +maybe(endtag(TAG))
    +maybe(''#r'[\n]*'
        +begtag('figcaption')
        +group(TAG+'cap')(to_next_tag())
        +endtag('figcaption')
        )
    +endtag('figure')
    )

image = media_regex('img')
video = media_regex('video')
audio = media_regex('audio')

prose = (''
    +begtag('p')
    +group('text')(r'[^\n]*')
    +endtag('p')
    )

content_item = '|'.join((
    image,
    video,
    audio,
    prose,
    ))

def get_items(html):
    return [mm.groupdict()
            for mm in re.finditer(content_item, html, flags=re.M)]

#==============================================================================
#===  TESTING  ================================================================
#==============================================================================

def test(p, verbose=False):
    bb = get_items(p)

    assert len(bb)>=1, 'found no match!'
    assert len(bb)<=1, 'found multiple matches!'

    if not verbose: return

    b = bb[0]
    for k,v in b.items():
        print('  '+k+'  '+str(v))
    print('-'*80)
    print()

if __name__=='__main__':
    with open(TEST_FILE) as f:
        html = f.read()
    paragraphs = [tt for tt in html.split('\n\n\n')
                  if tt and not tt.startswith('---')]
    for i, p in tqdm.tqdm(enumerate(paragraphs)):
        test(p)
    print('ALL OK!')
