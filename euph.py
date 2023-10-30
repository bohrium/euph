# author: samtenka
# change: 2023-10-28
# create: 2023-10-28
# descrp: scrape [ euphonics.org ] and assemble to book
# to use:

import urllib.request
import re
import numpy as np
import datetime
import tqdm

#-------  _  ------------------------------------------------------------------

GREEN = '\033[01m\033[32m'
LIME  = '\033[22m\033[32m'
GRAY  = '\033[90m'
UP    = '\033[1A'

#-------  _  ------------------------------------------------------------------

def clean_pre(s):
    return (s.replace(b'\xc2\xad', b'')
             .replace(b'<em>', b'')
             .replace(b'</em>', b'')
             )

def clean_post(s):
    #return s
    return (s.replace('&#x27;' , '`')
             .replace('&#039;' , '\'')
             .replace('&#8220;', '``' )
             .replace('&#8221;', '\'\'' )
             .replace('&#8216;', '`')
             .replace('&#8217;', '\'')
             .replace('&#8211;', '--')
             .replace('&nbsp;', '~')
             .replace('&#8212;', '---')
             #.replace('<strong>', '\\sampassage{')
             #.replace('</strong>', '}')
             )

user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
user_agent = 'Mozilla/5.0 (X11; Linux i686 on x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2909.25 Safari/537.36'
headers = {'User-Agent':user_agent,}

def get_headlines(url, pattern):
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request, timeout=2.)
    html = clean_pre(response.read())
    html = clean_post(html.decode('utf-8'))
    html = html.replace('_', '\\_')
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

import hashlib
import glob
import os

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
        elif text.startswith('<strong>'):
             text = (text.replace('<strong>', '\\samsection{')
                         .replace('</strong>', '}'))
        text = (text.replace('<strong>', '\\textbf{')
                    .replace('</strong>', '}'))
        #
        text = re.sub('<a rel[^>]*>', r'\\tt{}', text)
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
            #assert dur<60, 'video at {:s} too long!'.format(local_name)
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
figu = '<figure[^>]*><img( [a-z]+(="[^"]*")?)* src="(?P<figurl>[^"]*)"[^>]*>(</image>)?<figcaption>(?P<figcap>[^<]*)</figcaption></figure>'
vide = '<figure[^>]*><video( [a-z]+(="[^"]*")?)* src="(?P<vidurl>[^"]*)"[^>]*>(</video>)?<figcaption>(?P<vidcap>[^<]*)</figcaption></figure>'
para = '|'.join((text, figu, vide))

bb = get_headlines('https://euphonics.org/5-3-signature-modes-and-formants/', para)
#tt = ''
#for link, caption in bb:
#    tt += wrap_col('\\fig{{ {:s} }}{{ {:s} }}'.format(link, caption)) + '\n'
tt = '\n\n'.join(map(process_para, bb))
print(tt)
#tt = '\n\n'.join(wrap_col(par) for par in bb if is_good_par(par))
with open('out.tex', 'w') as f:
    f.write(tt)

