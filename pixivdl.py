import requests, re, os, sys
def dl(url, workdir, make_new_folder=True):
    # url is post's url
    # (parameters)
    image_suffix = ['png', 'jpg', 'jpeg', 'gif', 'PNG', 'JPG', 'JPEG', 'GIF']
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
              }
    if '/' not in url:  # given ID
        url = 'https://www.pixiv.net/en/artworks/'+url
    if not url.startswith('https://'):
        url = 'https://' + url
    if workdir in ['', './', '.']:
        workdir = url.split('/')[-1]
    if make_new_folder:
        os.system('mkdir {0}'.format(workdir))
    if workdir.endswith('/'):
        d = workdir
    else:
        d = workdir + '/'    
    
    # get page
    r = requests.get(url)
    if r.status_code!=200:
        print('cant fetch main page, code ', r.status_code)
        return -1
    for suffix in image_suffix:
        urls = re.findall('"https://i.pximg.net/img-original/img[/0-9_p]+.{0}"'.format(suffix), r.text)
        if len(urls)!=0:
            break
    else:
        print("cant fetch sample image")
        print('suffices tried:', image_suffix)
        return -1
    
    # get misc
    misc_page_count = misc_user_id = misc_user_name = 'void'
    tmp = re.findall('"pageCount":[0-9]+', r.text)
    misc_page_count = max([int(_.split(':')[-1]) for _ in tmp])
    misc_user_id = int(re.findall('"userId":"[0-9]+"', r.text)[0].split(':')[-1].replace('"', ''))
    print('{0} pages, author {1} ({2})'.format(misc_page_count, misc_user_name, misc_user_id))
    with open(d+'info', 'w') as file:
        file.write('guessed pagecount\t{0}\n'.format(misc_page_count))
        file.write('userid\t{0}\n'.format(misc_user_id))
    
    # get images
    url_sample = 'https://' + urls[0].split('https://')[-1].replace('"', '')
    print('sample image url is',  url_sample)
    headers['referer'] = url
    base_image_url = url_sample
    image_suffix = base_image_url.split('.')[-1]
    base_image_url = '_'.join(base_image_url.split('_')[:-1])
    
    for i in range(misc_page_count):
        r = requests.get(base_image_url+'_p{0}.{1}'.format(i, image_suffix), headers=headers)
        if r.status_code!=200:
            if r.status_code==404:
                print('(actual total page is {0})'.format(i+1))
                break
            print('error, code ', r.status_code, 'image:', i)
            continue
        with open(d+'{0}.{1}'.format(i, image_suffix), 'wb') as file:
            file.write(r.content)
    return 0
    
def main():
    if len(sys.argv)<2:
        print('usage: python thissrc.py [pixiv post url or id]')
        print('       Will create a folder named [id] in the current workdir.')
        return
    outdir = ''

    for url in sys.argv[1:]: 
        ret = dl(url, outdir)
    
        if ret==0:
            print('finished successfully')
        else:
            print('aborted')

if __name__=='__main__':
    main()
