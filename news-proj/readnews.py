import urllib.request
import re
import datetime

#   import ssl
#   try:
#       _create_unverified_https_context = ssl._create_unverified_context
#   except AttributeError:
#       # Legacy Python that doesn't verify HTTPS certificates by default
#       pass
#   else:
#       # Handle target environment that doesn't support HTTPS verification
#       ssl._create_default_https_context = _create_unverified_https_context

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
             .replace(b'.',        b''))

def clean_post(s):
    return (s.replace('&#x27;' , '\'')
             .replace('&#039;' , '\'')
             .replace('&#8220;', '"' )
             .replace('&#8221;', '"' )
             .replace('&#8216;', '\'')
             .replace('&#8217;', '\''))

user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
user_agent = 'Mozilla/5.0 (X11; Linux i686 on x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2909.25 Safari/537.36'
headers = {'User-Agent':user_agent,}

def get_headlines(url, pattern):
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request, timeout=2.)
    html = clean_pre(response.read())
    html = clean_post(html.decode('utf-8'))
    return [mm.group(1) for mm in re.finditer(pattern, html)]

#-------  _  ------------------------------------------------------------------

news_patterns = {
    ###('epgn.com/category/news/international', 3, 2., r'<h3 class="entry-title td-module-title">\s*<a href="[^"]*" rel="bookmark" title="[^"]*">\s*([^<^\n]*)\s*</a>\s*</h3>'),
    ###('epgn.com/category/news/international', 30, r'<a href="[^"]*" rel="bookmark" title=[^>]*>\s*([^<^\n]*)\s*</a>\s*</h3>'),
    ###('epgn.com/category/news/international', 30, r'>\s*([^<^\n]*)\s*</a>\s*</h3>'),
    ###('epgn.com/category/news/national', 3, 0.3, r'</div>[^<]*<h3 class="entry-title td-module-title">\s*<a[^<]*>\s*([^<^\n]*)\s*</a>\s*</h3>'),
    ###('spectrum.ieee.org/type/news/', 5, 0.9, r'<a class="widget__headline-text custom-post-headline" href="[^"]*" aria-label="[^"]*" data-type="text">\s*([^<^\n]*)\s*</a></h2>'),
    ###('theatlantic.com/politics', 3, 2.7, r'</h2></a><p[^<]*>([^<^\n]*)</p>'),
    ('aljazeera.com/africa', 3, 0.3, r'<span>([^<^\n]*)</span></a></h3></div><'),
    ('aljazeera.com/asia', 3, 0.3, r'<span>([^<^\n]*)</span></a></h3></div><'),
    ('aljazeera.com/economy', 3, 0.3, r'<span>([^<^\n]*)</span></a></h3></div><'),
    ('aljazeera.com/middle-east', 3, 0.9, r'<span>([^<^\n]*)</span></a></h3></div><'),
    ('aljazeera.com/us-canada', 3, 0.3, r'<span>([^<^\n]*)</span></a></h3></div><'),
    ('asahi.com/ajw/asia_world/around_asia', 3, 0.3, r'<p class="title">([^<^\n]*)</p>\s*<p class="date">'),
    ('asahi.com/ajw/asia_world/china', 3, 0.3, r'<p class="title">([^<^\n]*)</p>\s*<p class="date">'),
    ('asahi.com/ajw/asia_world/world', 3, 0.3, r'<p class="title">([^<^\n]*)</p>\s*<p class="date">'),
    ('asamnews.com', 3, 2.7, r'<a href="[^"]*" rel="bookmark" title="[^"]*">([^<^\n]*)</a></h3>'),
    ('bigthink.com', 1, 0.9, r'<div class="card-headline">\s*<a href="[^"]*">([^<^\n]*)</a></div>'),
    ('csmonitor.com/usa', 3, 0.9, r'<h3 class="story-headline">\s*<span class="story_link">([^/^\n]*)</span>'),
    ('csmonitor.com/world', 3, 0.9, r'<h3 class="story-headline">\s*<span class="story_link">([^/^\n]*)</span>'),
    ('csmonitor.com/world/topics/news-and-values', 3, 0.9, r'<h3 class="story-headline">\s*<span class="story_link">([^/^\n]*)</span>'),
    ('economist.com/finance-and-economics', 3, 0.3, r'"headline":"([^"]*)","image"'),
    ('economist.com/science-and-technology', 3, 2.7, r'"headline":"([^"]*)","image"'),
    ('economist.com/united-states', 3, 0.3, r'"headline":"([^"]*)","image"'),
    ('herald.co.zw/category/articles/international', 5, 0.9, r'class="btn-link">([^<^\n]*)</a></h3>'),
    ('jakartaglobe.id/news', 1, 0.3, r'<h3 class="mt-3 text-white">([^<^\n]*)</h3>'),
    ('jakartaglobe.id/news', 3, 0.3, r'<span class="text-white text-truncate-2-lines">([^<^\n]*)</span></div>'),
    ('nature.com/news', 5, 2.7, r'<h3 class="c-card__title u-serif u-text17 u-font-weight--regular">([^<^\n]*)</h3>'),
    ('news24.com/fin24/climate_future', 1, 0.9, r'data-event-breadcrumb="[-/_a-z0-9]*">\s*<span>([^<^\n]*)</span>'),
    ('news24.com/fin24/climate_future', 3, 0.9, r'<div class="article-item__title">\s*<span>\s*([^W]|(W[^A])[^<^\n]*)\s*</span>\s*</div>'),
    ('news24.com/news24/africa', 1, 0.3, r'data-event-breadcrumb="[-/_a-z0-9]*">\s*<span>([^<^\n]*)</span>'),
    ('news24.com/news24/africa', 3, 0.3, r'<div class="article-item__title">\s*<span>\s*([^W]|(W[^A])[^<^\n]*)\s*</span>\s*</div>'),
    ('news24.com/news24/tech-and-trends', 1, 0.3, r'data-event-breadcrumb="[-/_a-z0-9]*">\s*<span>([^<^\n]*)</span>'),
    ('news24.com/news24/tech-and-trends', 3, 0.3, r'<div class="article-item__title">\s*<span>\s*([^W]|(W[^A])[^<^\n]*)\s*</span>\s*</div>'),
    ('news24.com/news24/world', 1, 0.3, r'data-event-breadcrumb="[-/_a-z0-9]*">\s*<span>([^<^\n]*)</span>'),
    ('news24.com/news24/world', 3, 0.3, r'<div class="article-item__title">\s*<span>\s*([^W]|(W[^A])[^<^\n]*)\s*</span>\s*</div>'),
    ('newsone.com/category/news/politics', 3, 2.7, r'<h2 class="ione4-block-title-text">\s*<a href="[^"]*" class="page-card ione4-link">\s*([^<^\n]*)\s*</a>\s*</h2>'),
    ('newyorker.com/news', 3, 0.9, r'<h[1-4] class="(?:Hero|River)__[^"]*">([^<^\n]*)</h[1-4]></a>'),
    ('npr.org/sections/science', 5, 0.9, r'>([^<^\n]*)</a></h2>'),
    ('nymag.com/intelligencer/', 5, 0.9, r'<h2 class="lede-headline">([^<]*)</h2>'),
    ('nytimes.com', 1, 0.3, r'<h3 class="[- a-z0-9]*">([^<^\n]*)</h3></div'),
    ('nytimes.com/section/world/africa', 3, 0.9, r'<h3 class="css-[ a-z0-9]*">([^<^\n]*)</h3><p'),
    ('nytimes.com/spotlight/latin-america', 3, 0.9, r'<h3 class="css-[ a-z0-9]*">([^<^\n]*)</h3><p'),
    ('pambazuka.org', 5, 2.7, r'<div class="views-field views-field-title">\s*<span class="field-content"><a href="[^"]*">([^<^\n]*)</a></span>\s*</div>'),
    ('pewresearch.org', 5, 0.9, r'/\'>([^<^\n]*)</a></h[12]>'),
    ('phys.org', 5, 2.7, r'<h3(?:| class="text-large mt-2 mb-1")>([^<^\n]*)</h3>'),
    ('quantamagazine.org', 5, 2.7, r'<h3[^<]*>([^<^\n]*)</h3>'),
    ('reason.com', 1, 1., r'data-ga-label="[^"]*">\s*([^<]*)\s*</a>\s*</h1>'),
    ('reason.com', 3, 1., r'data-ga-label="[^"]*">\s*([^<]*)\s*</a>\s*</h[234]>'),
    ('riotimesonline.com/brazil-news/category/mercosur', 3, 0.3, r'rel="bookmark" title="[^"]*">([^<^\n]*)</a></h3>'),
    ('riotimesonline.com/brazil-news/category/modern-day-censorship', 3, 2.7, r'rel="bookmark" title="[^"]*">([^<^\n]*)</a></h3>'),
    ('riotimesonline.com/brazil-news/category/new-multipolar-world-order', 3, 2.7, r'rel="bookmark" title="[^"]*">([^<^\n]*)</a></h3>'),
    ('sanjuandailystar.com/all-news/categories/international', 3, 0.9, r'36\)">([^<^\n]*)</p></div></div></a>'),
    ('sanjuandailystar.com/all-news/categories/viewpoint', 3, 0.9, r'36\)">([^<^\n]*)</p></div></div></a>'),
    ('science.org/news', 1, 2.7, r'<h3 class="grid-hero-teaser__title mb-2">\s*<a href="[^"]*" title="[^"]*">([^<^\n]*)</a>\s*</h3>'),
    ('science.org/news', 5, 2.7, r'<div class="card-header mb-2">\s*<a href="[^"]*"\s*title="[^"]*"\s*class="[^"]*">\s*([^<^\n]*)\s*</a>\s*</div>'),
    ('scitechdaily.com',5, 2.7, r'<span class=ticker-item-title>([^<^\n]*)</span></a>'),
    ('scotusblog.com',5, 0.3, r'>([^<^\n]*)</a></h[12]>'),
    ('smh.com.au/environment/climate-change', 3, 0.3, r'>([^<^\n]*)</a></h3><p '),
    ('smh.com.au/world', 3, 0.3, r'>([^<^\n]*)</a></h3><p '),
    ('smh.com.au/world/africa', 3, 0.3, r'>([^<^\n]*)</a></h3><p '),
    ('smh.com.au/world/middle-east', 3, 0.3, r'>([^<^\n]*)</a></h3><p '),
    ('smh.com.au/world/north-america', 3, 0.3, r'>([^<^\n]*)</a></h3><p '),
    ('spectator.co.uk/category/international', 3, 0.9, r'<a class="article__title-link" href="[^"]*">\s*([^<^\n]*)\s*</a>\s*</h3>'),
    ('spiegel.de/international/europe', 3, 0.9, r'<span class="[-:a-z ]*align-middle[-:a-z ]*">([^<^\n]*)</span>'),
    ('spiegel.de/international/tomorrow', 3, 0.3, r'<span class="[-:a-z ]*align-middle[-:a-z ]*">([^<^\n]*)</span>'),
    ('spiegel.de/international/world', 3, 0.3, r'<span class="[-:a-z ]*align-middle[-:a-z ]*">([^<^\n]*)</span>'),
    ('spiegel.de/international/zeitgeist', 3, 0.9, r'<span class="[-:a-z ]*align-middle[-:a-z ]*">([^<^\n]*)</span>'),
    ('theatlantic.com/projects/planet/', 3, 0.9, r'class="ProjectGrid_link__[^"]*">([^<^\n]*)</a></h2>'),
    ('thebureauinvestigates.com/stories/', 3, 0.9, r'>([^<^\n]*)</h2>'),
    ('them.us/news', 3, 0.9, r'data-testid="SummaryItemHed">([^<^\n]*)</h3>'),
    ('them.us/news/politics', 3, 0.9, r'data-testid="SummaryItemHed">([^<^\n]*)</h3>'),
    ('timesofindia.indiatimes.com/world', 3, 0.3, r'name":"([^"^\n]*)"\n'),
    ('timesofindia.indiatimes.com/world/south-asia', 3, 0.9, r'name":"([^"^\n]*)"\n'),
    ('wsj.com/news/opinion', 3, 0.3, r'<span class="WSJTheme--headlineText--[a-zA-Z0-9]* ">([^<^\n]*)</span></a></h[23]></div>'),
    ('wsj.com/news/us', 3, 0.3, r'<span class="WSJTheme--headlineText--[a-zA-Z0-9]* ">([^<^\n]*)</span></a></h[23]></div>'),
}

#-------  _  ------------------------------------------------------------------

with open('words') as f:
    words = set(f.read().split())

def get_headlines_by_url_and_keywords(kw_threshold=3, __VERBOSE__=True):

    # collect (url, headline, wordbags) tuples
    url_headline_wordbags = []
    headlines = set()
    if __VERBOSE__: print()
    for url, n, imp, pattern in sorted(news_patterns):
        if __VERBOSE__: print(UP+GRAY+'reading ('+url+')'+' '*50)
        try:
            hs = get_headlines('https://www.'+url, pattern)
            for h in hs[:n]:
                if h in headlines: continue
                url_headline_wordbags.append((url,h,set(h.split()), imp))
                headlines.add(h)
        except (TimeoutError,
                urllib.error.HTTPError,
                urllib.error.URLError  ) as e:
            if __VERBOSE__: print(UP+GRAY+'could not read ('+url+')'+' '*50+'\n\n')
    if __VERBOSE__: print(UP+GRAY+'done reading'+' '*100)

    # collect keywords
    is_important = lambda w: (5<=len(w) and w[0].isupper()) or 7<=len(w)
    is_common    = lambda w: w.lower() in words
    is_lowercase = lambda w: w.islower()
    #importantwords = {w for _,_,ws,_ in url_headline_wordbags for w in ws if is_important(w)}
    importantwords = {w for _,_,ws,_ in url_headline_wordbags for w in ws}
    counts = {w:0 for w in importantwords}
    for _,h,ws,imp in url_headline_wordbags :
        for w in ws:
            #if not is_important(w): continue
            counts[w] += (imp * ( .2 if is_common(w)    else 1. )
                              * (1.  if is_important(w) else  .5)
                              * (.1  if h.endswith('?') else 1. ) # questions are bad
                              * ( .5 if is_lowercase(w) else 1. ))
    counts = sorted([(n,w) for w,n in counts.items()], reverse=True)
    keywords = [w for n,w in counts if kw_threshold<=n]
    keywords_set = set(keywords)

    # select keyword-relevant headlines
    url_headline_wordbags = [(url,h,ws,imp)
                             for (url,h,ws,imp) in url_headline_wordbags
                             if ws.intersection(set(keywords))      ]

    # organize headlines by url
    by_url = {}
    for url,h,_,_ in url_headline_wordbags:
        if url not in by_url: by_url[url]=[]
        by_url[url].append(h)

    return (by_url, keywords)

#-------  _  ------------------------------------------------------------------

def today():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def print_nicely(by_url, keywords):
    print('; '.join(keywords[:7])+'...')
    keywords_set = set(keywords)
    for url in by_url:
        for h in by_url[url]:
            h = ' '.join(((GREEN+w+LIME) if w in keywords_set else w)
                         for w in h.split()                      )
            print((LIME+h+GRAY).ljust(100+5*h.count('\033'),'.')+'('+url+')')

    print(GRAY+'and that is today\'s news ({})!'.format(today()))

if __name__=='__main__':
    by_url, keywords = get_headlines_by_url_and_keywords(3.5)
    print_nicely(by_url, keywords)
