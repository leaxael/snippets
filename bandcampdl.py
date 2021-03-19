import requests, re, os, sys

def dl_bandcamp(url, make_new_folder=True):
    esc = str.maketrans('| ></"\'', '_______')
    info = requests.get(url)

    if info.status_code!=200:
        print('ERROR: cant get info page, code {0}'.format(info.status_code))
        return -1

    # meta
    tracknames = [_.split('track-title">')[1].split('</span>')[0].replace('\u3000', ' ').replace(' ', '_') for _ in \
             re.findall('<span class="track-title">.+</span></a>', info.text)]
    albumname = re.findall('<title>.+</title>', info.text)[0].split('<title>')[1].split('</title>')[0]
    albumname = albumname.replace('\u3000', ' ')
    albumname = albumname.translate(esc)
    urls = re.findall('"https://t4.bcbits.com/stream[a-zA-Z0-9\-\?\=\&\/_]+', info.text)

    # sancheck
    sanpass = True
    if len(urls)!=len(tracknames):
        print('WARNING: got {0} track names but {1} track urls'.format(len(tracknames), len(urls)))
        print('         continue anyway with arbitrary file naming')
        sanpass = False
    else:
        print('got {0} tracks to download'.format(len(tracknames)))

    if make_new_folder:
        os.system('mkdir {0}'.format(albumname))  # should be rather safe

    # download
    for i, url in enumerate(urls):
        if sanpass:
            fn = 'track{0}_'.format(i)+tracknames[i]
        else:
            fn = 'track{0}'.format(i)
        a = requests.get(url[1:])
        if a.status_code!=200:
            print('ERROR: failed on {0}'.format(fn))
            continue
        with open('{0}/{1}.mp3'.format(albumname, fn), 'wb') as file:
            file.write(a.content)
    return 0

def main():
    if len(sys.argv)<2:
        print('usage: python thissrc.py [bandcamp url]')
        print('       Will create a folder named by the album title in the workdir.')
        print('       (Escape characters are reasonably safely handled, see code if not sure.)')
        return

    for url in sys.argv[1:]:
        ret = dl_bandcamp(url)

        if ret==0:
            print('finished successfully')
        else:
            print('aborted')

if __name__=='__main__':
    main()

