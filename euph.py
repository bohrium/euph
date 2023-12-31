# author:   samtenka
# change:   2023-11-016
# create:   2023-10-28
# descrp:   scrape [ euphonics.org ] and assemble to book
# to use:
#   PREREQS Make directories `fig`, `vid`, and `body`.  Also make sure you have
#           `main.tex` and `sam.sty`.  This project depends also on `ffmpeg`
#           and its sister `ffprobe`; on python libries `urllib` (and to a tiny
#           extent `numpy` and `tqdm`).
#
#   STITCH  Then run `python3 euph.py`.  This will download text, images,
#           videos from euphonics.org, take a few frames from each video to
#           make more images, and create a file `all-inputs.tex` and a
#           bunch of file `body/*.tex`.
#
#   TYPESET Then run `pdflatex main.tex`.  This should create `main.pdf`, which
#           you open and enjoy.

import urllib.request
import re
import numpy as np
import tqdm
import hashlib
import glob
import os
from parse_html import get_items, content_item , urls

#-------  _  ------------------------------------------------------------------

def clean_pre(s):
    return (s.replace(b'\xc2\xad', b'')
             .replace(b'<em>', b'')
             .replace(b'</em>', b'')
             )

def clean_post(s):
    return (s.replace('&#x27;' , '`')
             .replace('&#039;' , '\'')
             .replace('&#8220;', '``' )
             .replace('&#8221;', '\'\'' )
             .replace('&#8216;', '`')
             .replace('&#8217;', '\'')
             .replace('&#8211;', '--')
             .replace('&nbsp;', '~')
             .replace('&#8212;', '---')
             #
             .replace('&#8230;', '...')
             .replace('&gt;', '>')
             .replace('&lt;', '<')
             .replace('&amp;', '\\&')
             #
             #.replace('%', r'\%')
             #
            .replace('<strong>', '\\textbf{')
            .replace('</strong>', '}')
            .replace('<br>', '')
             )

#user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
user_agent = 'Mozilla/5.0 (X11; Linux i686 on x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2909.25 Safari/537.36'
headers = {'User-Agent':user_agent,}

def get_headlines(url, pattern, clean_percents=False):
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request, timeout=2.)
    html = clean_pre(response.read())
    html = clean_post(html.decode('utf-8'))
    if clean_percents:
        html = re.sub(r'(?<=[^\\])%', r'\\%', html)
    return [mm.groupdict()
            for pp in html.split('\n\n')
            for mm in re.finditer(pattern, pp)]

def wrap_col(text, line_width=80, indent='  '):
    formatted = indent[:]
    col = len(indent)
    for word in filter(None, text.split(' ')):
        l = len(word+' ')
        if col+l > line_width:
            formatted += '\n' + indent
            col = len(indent)
        formatted += word+' '
        col += l
    return formatted

def process_para(groupdict):
    gd = groupdict
    text = gd['text']
    imageurl = gd['imgurl']
    imagecap = gd['imgcap']
    videourl = gd['videourl']
    videocap = gd['videocap']
    audiourl = gd['audiourl']
    audiocap = gd['audiocap']

    if text is not None:
        if 'SECTION' in text: return ''
        text = text.strip()
        #
        if text.startswith('$$') and text.endswith('$$'):
            text = r'\begin{equation*}' + text[2:-2] + r'\end{equation*}'
        elif text.startswith('[1]'):
            text = '\\sectionreferences{}'+text
        elif text and text[0].islower():
            text = r'\noindent{}'+text
        #elif text.startswith('<strong>'):
        #     text = (text.replace('<strong>', '\\samsection{')
        #                 .replace('</strong>', '}'))
        #text = (text.replace('<strong>', '\\textbf{')
        #            .replace('</strong>', '}'))
        #
        text = re.sub('<a [^>]*>', r'\\tt{}', text)
        text = re.sub('</a>', r'\\rm{}', text)
        text = text.replace('Fig. ', 'Fig.\\ ')
        text = text.replace('Figs. ', 'Figs.\\ ')
        #
        return wrap_col(text)

    elif imageurl is not None:
        h = hashlib.md5(imageurl.encode('utf-8')).hexdigest()[:8]
        local_name = 'figs/fig-{:s}.png'.format(h)
        if not glob.glob(local_name):
            print('downloading {:s}'.format(imageurl))
            os.system('curl -o {:s} {:s} -s'.format(local_name, imageurl))
        imagecap = '\\caption{{{:s}}}'.format(imagecap.strip()) if imagecap is not None else ''
        imagecap = re.sub('<(/)?a[^>]*>', '', imagecap)
        imagecap = re.sub('<a [^>]*>', r'\\tt{}', imagecap)
        imagecap = re.sub('</a>', r'\\rm{}', imagecap)
        imagecap = imagecap .replace('_','\\_') # TODO FIXME : what if mathmode subscript?

        return wrap_col('\\fig{{{:s}}}{{{:s}}}'.format(local_name, imagecap))
    elif videourl is not None:
        h = hashlib.md5(videourl.encode('utf-8')).hexdigest()[:8]
        local_name = 'vids/vid-{:s}.png'.format(h)
        if not glob.glob(local_name):
            print('downloading {:s}'.format(videourl))
            os.system('curl -o {:s} {:s} -s'.format(local_name, videourl))
            temp_out = 'temp-out'
            os.system('ffprobe -i {:s} -show_entries format=duration -v quiet -of csv="p=0" > {:s}'.format(local_name, temp_out))
            with open(temp_out) as f:
                dur = float(f.read())
                print('{:.2f} seconds'.format(dur))

            for i,t in enumerate(np.linspace(0., dur, num=3, endpoint=False)):
                frame_name = 'vids/vid-{:s}-{:02d}.png'.format(h, i)
                os.system('ffmpeg -ss {:02.2f} -i {:s} -frames:v 1 {:s} -hide_banner -loglevel error'.format(t, local_name, frame_name))

        frame_names = sorted(glob.glob('vids/vid-{:s}-*.png'.format(h)))
        ll = len(frame_names)
        videocap = '\\caption{{{:s}}}'.format(videocap.strip()) if videocap is not None else ''
        videocap = re.sub('<(/)?a[^>]*>', '', videocap)
        videocap = re.sub('<a [^>]*>', r'\\tt{}', videocap)
        videocap = re.sub('</a>', r'\\rm{}', videocap)
        videocap = videocap.replace('_','\\_') # TODO FIXME : what if mathmode subscript?

        return '\\moobeginvid\\begin{{tabular}}{{{:s}}} {:s} \\end{{tabular}}{:s}\\mooendvideo'.format(
            'c'*ll,
            '&'.join('\\vidframe{{ {:.2f} }}{{ {:s} }}'.format(.9/ll, fn) for fn in frame_names),
            videocap
        )
    elif audiourl is not None:
        h = hashlib.md5(audiourl.encode('utf-8')).hexdigest()[:8]
        extn = audiourl.split('.')[-1]
        local_name = 'auds/aud-{:s}.{:s}'.format(h, extn)
        plot_name = 'auds/aud-{:s}-plot.png'.format(h)

        if not glob.glob(local_name):
            print('downloading {:s}'.format(audiourl))
            os.system('curl -o {:s} {:s} -s'.format(local_name, audiourl))
            os.system('python3 render_audio.py {:s} {:s}'.format(local_name, plot_name))

        audiocap = '\\caption{{{:s}}}'.format(audiocap.strip()) if audiocap is not None else ''
        audiocap = re.sub('<(/)?a[^>]*>', '', audiocap)
        audiocap = re.sub('<a [^>]*>', r'\\tt{}', audiocap)
        audiocap = re.sub('</a>', r'\\rm{}', audiocap)
        audiocap = audiocap.replace('_','\\_') # TODO FIXME : what if mathmode subscript?

        return wrap_col('\\aud{{{:s}}}{{{:s}}}'.format(plot_name, audiocap))

    else:
        assert False

def tex_from(url, texname):
    bb = get_headlines(url, content_item, clean_percents=True)
    tt = '\n\n'.join(map(process_para, bb))
    with open(texname, 'w') as f:
        f.write(tt)

bb = get_headlines('https://euphonics.org/homepage/', urls)
for b in bb:
    print(b)

filenm_from_sn = lambda sectnum : 'body/body.{:s}.tex'.format(sectnum.replace('.', '-'))

def make_input(b):
    sn = b['sectnum'].replace('.', '-')
    title = b['title']
    level = sn.count('-')
    h = hashlib.md5(title.encode('utf-8')).hexdigest()[:8]
    return (''
        +{0:'\\sampart', 1:'\\samsection', 2:'\\sampassage'}[level]
        +'{{{:s} \\quad {:s}}}'.format(sn, b['title'])
        +r'\label{s:'+h+'}'
        +'\\renewcommand{{\\whichsect}}{{{:s}}}'.format(sn)
        +'\\input{{{:s}}}'.format(filenm_from_sn(sn))
    )

def make_contents(b):
    sn = b['sectnum'].replace('.', '-')
    title = b['title']
    level = sn.count('-')
    h = hashlib.md5(title.encode('utf-8')).hexdigest()[:8]
    return (
         {0:r'\item[\hspace{{-1cm}}{{\gre{{}}{:s}}}\hspace{{+0cm}} \large\bf\sf \blu {:s}]\hfill \\ ',
         1:r'\quad{{\gre {:s}}}~{:s}',
         #1:r'\item[\quad\quad {:s}]\hfill {:s}',
         2:''}[level].format(
            r'\pageref{s:'+h+'}',
            title,
        )
    )

def make_all_inputs(allfilename, contentsfilename=None):
    all = '\n'.join(map(make_input, bb))
    with open(allfilename, 'w') as f:
        f.write(all)

    if contentsfilename is None: return
    contents = (
        r'\begin{description}'
        +'\n'.join(filter(None, map(make_contents, bb)))
        +r'\end{description}'
        )
    with open(contentsfilename, 'w') as f:
        f.write(contents)


def make_all_bodies():
    for b in tqdm.tqdm(bb):
        url = b['url']
        sectnum = b['sectnum']
        #if sectnum not in ['3.6','4.2','9.1', '9.3.2', '10.5']: continue
        #if not sectnum.startswith('11'): continue
        tex_from(url, filenm_from_sn(sectnum))

def correct_typo(sectnum, before, after):
    fnm = 'body/body.{:s}.tex'.format(sectnum.replace('.','-'))
    with open(fnm, 'r') as f:
        t = f.read()
        t = t.replace(before, after)
        #t = re.sub(before, after, t)
    with open(fnm, 'w') as f:
        f.write(t)

def correct_all(sectnum, before, after):
    for b in bb:
        sn = b['sectnum']
        correct_typo(sn, before, after)
        #correct_typo(sn, '<a [^>]*>', r'\\tt{}')

if __name__=='__main__':
    make_all_inputs('all-input.tex', contentsfilename='all-contents.tex')
    make_all_bodies()

    correct_typo('5.5', r'admittances are plotted in Fig.\ 15}.',
                        r'admittances are plotted in Fig.\ 15.'  )
    correct_typo('6.4', r'Technical Report #1998-010,' ,
                        r'Technical Report \#1998-010,' )
    correct_typo('11.8',r'middle D#',
                        r'middle D\#' )
    #correct_typo('1', r'http://campusdata.uark.edu/resources/images/articles/2017-01-31_04-23-17-PMRS61352_KellyBros-scr.jpg',
    #                  r'')

