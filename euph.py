# author:   samtenka
# change:   2023-10-30
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
             .replace('%', '\\%')
             )

user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
user_agent = 'Mozilla/5.0 (X11; Linux i686 on x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2909.25 Safari/537.36'
headers = {'User-Agent':user_agent,}

def get_headlines(url, pattern):
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request, timeout=2.)
    html = clean_pre(response.read())
    html = clean_post(html.decode('utf-8'))
    return [mm.groupdict() for mm in re.finditer(pattern, html)]

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
    figurl = gd['figurl']
    figcap = gd['figcap']
    vidurl = gd['vidurl']
    vidcap = gd['vidcap']
    if text is not None:
        if 'SECTION' in text: return ''
        text = text.strip()
        #
        if text.startswith('[1]'):
            text = '\\sectionreferences{}'+text
        #elif text.startswith('<strong>'):
        #     text = (text.replace('<strong>', '\\samsection{')
        #                 .replace('</strong>', '}'))
        text = (text.replace('<strong>', '\\textbf{')
                    .replace('</strong>', '}'))
        #
        text = re.sub('<a [^>]*>', r'\\tt{}', text)
        text = re.sub('</a>', r'\\rm{}', text)
        text = text.replace('Fig. ', 'Fig.\\ ')
        text = text.replace('Figs. ', 'Figs.\\ ')
        #
        return wrap_col(text)
    elif figurl is not None:
        h = hashlib.md5(figurl.encode('utf-8')).hexdigest()[:8]
        local_name = 'figs/fig-{:s}.png'.format(h)
        if not glob.glob(local_name):
            print('downloading {:s}'.format(figurl))
            os.system('curl -o {:s} {:s} -s'.format(local_name, figurl))
        return wrap_col('\\fig{{{:s}}}{{{:s}}}'.format(local_name, figcap.strip()))
    elif vidurl is not None:
        h = hashlib.md5(vidurl.encode('utf-8')).hexdigest()[:8]
        local_name = 'vids/vid-{:s}.png'.format(h)
        if not glob.glob(local_name):
            print('downloading {:s}'.format(vidurl))
            os.system('curl -o {:s} {:s} -s'.format(local_name, vidurl))
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
        return '\\moobeginvid\\begin{{tabular}}{{{:s}}} {:s} \\end{{tabular}}\\caption{{{:s}}}\\mooendvideo'.format(
            'c'*ll,
            '&'.join('\\vidframe{{ {:.2f} }}{{ {:s} }}'.format(.9/ll, fn) for fn in frame_names),
            vidcap.strip()
        )
    else:
        assert False

text = '<p>(?P<text>[^\n]*)</p>'
figu = '(<div [^>]*>)?<figure[^>]*><img( [a-z]+(="[^"]*")?)* src="(?P<figurl>[^"]*)"[^>]*>(</image>)?<figcaption [^>]*>(?P<figcap>[^<]*)</figcaption></figure>'
vide = '(<div [^>]*>)?<figure[^>]*><video( [a-z]+(="[^"]*")?)* src="(?P<vidurl>[^"]*)"[^>]*>(</video>)?<figcaption [^>]*>(?P<vidcap>[^<]*)</figcaption></figure>'
para = '|'.join((text, figu, vide))

def tex_from(url, texname):
    bb = get_headlines(url, para)
    tt = '\n\n'.join(map(process_para, bb))
    with open(texname, 'w') as f:
        f.write(tt)


urls = '<p[^>]*>(<mark [^>]*>Chapter )?(?P<sectnum>[0-9]+(.[0-9]+)*)(</mark>)? <a [^>]*href="(?P<url>[^"]*)"[^>]*>(?P<title>[^<]*)</a></p>'

bb = get_headlines('https://euphonics.org/homepage/', urls)

filenm_from_sn = lambda sectnum : 'body/body.{:s}.tex'.format(sectnum.replace('.', '-'))

def make_input(b):
    sn = b['sectnum'].replace('.', '-')
    title = b['title']
    level = sn.count('-')
    return (
        {0:'\\sampart', 1:'\\samsection', 2:'\\sampassage'}[level]+
        '{{{:s} \\quad {:s}}}'.format(sn, b['title']) +
        '\\renewcommand{{\\whichsect}}{{{:s}}}'.format(sn) +
        '\\input{{{:s}}}'.format(filenm_from_sn(sn))
    )

def make_all_inputs(allfilename):
    all = '\n'.join(map(make_input, bb))
    with open(allfilename, 'w') as f:
        f.write(all)

def make_all_bodies():
    for b in tqdm.tqdm(bb):
        url = b['url']
        sectnum = b['sectnum']
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

#print(bb)
if __name__=='__main__':
    make_all_inputs('all-input.tex')

    make_all_bodies()

    #correct_typo('4.3', r'frequency 10% below critical' ,
    #                    r'frequency 10\% below critical' )
    correct_typo('5.5', r'admittances are plotted in Fig.\ 15}.',
                        r'admittances are plotted in Fig.\ 15.'  )
    correct_typo('6.4', r'Technical Report #1998-010,' ,
                        r'Technical Report \#1998-010,' )
    correct_typo('11.8',r'middle D#',
                        r'middle D\#' )



