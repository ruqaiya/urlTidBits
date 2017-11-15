"""Main views module."""

from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
import whois

import json
import socket
from geopy.geocoders import Nominatim

import hashlib
import hmac
import base64

# Create your views here.


def home(request):
    """Main home view."""
    context = {}

    if request.method == 'POST':
        raw_url = request.POST['url']
        half_url = raw_url.split('//')[1]
        try:
            ip = get_ip(half_url)
        except:
            ip = None

        if ip is not None:
            url_ip = 'http://' + ip
            meta_tags = get_meta_tags(url_ip)
            address_data = get_address(ip)
            social_media_handles = get_social_media_handles(raw_url)
        else:
            ip = 'error'
            meta_tags = None
            address_data = None
            social_media_handles = None

        # url = 'https://'+request.POST['url']
        admin_contact = get_admin_contact(raw_url, half_url)

        alexarank = alexa_rank(half_url)

        # testing MOZ api

        try:
            moz_results = get_moz_details(request.POST['url'])
        except:
            moz_results = {}
            print('moz did not work')

        # get_ecommerce_site(request.POST['url'])

        context.update({
            'meta_tags': meta_tags,
            'alexarank': alexarank,
            'companyInfo': address_data,
            'socialmedia': social_media_handles,
            'admincontact': admin_contact,
            'ip': ip,
            'response': True,
            'raw_url': raw_url,
            'moz_results': moz_results,
        })
    else:
        pass

    return render(request, 'home.html', context)


def get_meta_tags(ip):
    """
    Getting meta tags by scraping through the page.

    Looking for the particular tags.
    """
    try:
        response = requests.get(ip)
        soup = BeautifulSoup(response.content, "html.parser")
        metas = soup.find_all('meta')

        meta_tag_content = {}
        for meta in metas:
            if 'name' in meta.attrs:
                meta_tag_content[meta.attrs['name']] = meta.attrs['content']

        response = requests.get(ip)
        soup = BeautifulSoup(response.content, "html.parser")

        title_tag = soup.find_all('title')

        for title in title_tag:
            title_text = title.text
            meta_tag_content['title'] = title_text

        return meta_tag_content
    except:
        return None


def alexa_rank(url):
    """
    Parsing XML from data.alexa.com.

    Taking alexa rank out of it.
    """
    try:
        alexa_rank_url = "http://data.alexa.com/data?cli=10&dat=s&url=" + url
        r = requests.get(alexa_rank_url)
    except:
        bs = None
    try:
        bs = BeautifulSoup(r.content, "xml").find("REACH")['RANK']
    except:
        bs = 'No rank is available for this site.'

    return bs


def get_admin_contact(url, half_url):
    """
    I am simply calling whois library to get contact name and email.

    Ideally wanted to traverse https://www.whois.com/whois/ for this
    information since whois library does not return the whole information.
    """
    data = {}

    try:
        w = whois.whois(url)
    except:
        pass

    # adding each data element in a seperate try/catch so nothing is missed and
    # all data that is available is extracted.
    try:
        data['name'] = w['name']
    except:
        pass

    try:
        data['email'] = w['email']
    except:
        pass

    try:
        data['email'] = w['emails']
    except:
        pass

    # Traversing Who is
    # whois_url = 'https://www.whois.com/whois/'+ half_url
    # response = requests.get(whois_url)
    # # print(response.content)
    # soup = BeautifulSoup(response.content, "html.parser")
    # raw_data = soup.find(id = 'registrarData')

    # print(type(raw_data.contents[0]))

    # print(type(raw_data))
    # # print(raw_data)

    # raw_data = raw_data.splitlines()

    # for line in raw_data:
    #     print('in line')
    #     print(line)

    return data

# GET CONTACT DETAILS + STREET ADDRESS + TIMEZONE ##########################


def get_address(ip):
    """Get address info."""
    # getting Country, co-ordinates and street address from ipinfo
    try:
        url = 'https://ipinfo.io/' + ip + '/json'
        r = requests.get(url)
        data = json.loads(r.content.decode('utf-8'))

        location = data['loc']
        geolocator = Nominatim()
        location = geolocator.reverse(location)
        data['address'] = location.address
    except:
        data = {}

    # getting timezone from geoip
    try:
        free_geo_ip_url = 'http://freegeoip.net/json'
        url = '{}/{}'.format(free_geo_ip_url, ip)
        response = requests.get(url)
        response_data = response.json()
        data['timezone'] = response_data['time_zone']
    except:
        pass

    return data

# GET IP FROM URL ######################


def get_ip(url):
    """Get ip from url."""
    try:
        ip = get_ips_for_host(url)
        return(ip[2][0])
    except:
        ip = None

    return ip


def get_ips_for_host(host):
    """Get IP from Host."""
    try:
        ips = socket.gethostbyname_ex(host)
    except socket.gaierror:
        ips = []
    return ips

# GET SOCIAL MEDIA HANDLES ##############################


def get_social_media_handles(url):
    """
    TO-DO: need to ignore the main site if the url is of the same social site.

    For eg if the url to test is Facebook.com we need to remove facebook.com
    from sm_sites list.
    """
    try:
        r = requests.get(url)
        # print(r.content)
        sm_sites = ['twitter.com', 'facebook.com', 'plus.google.com',
                    'pinterest.com', 'instagram.com']
        sm_sites_present = []

        soup = BeautifulSoup(r.content, 'html5lib')
        all_links = soup.find_all('a', href=True)

        for sm_site in sm_sites:
            for link in all_links:
                if sm_site in link.attrs['href']:
                    sm_sites_present.append(link.attrs['href'])

        return sm_sites_present
    except:
        return None


def get_moz_details(url):
    """Moz Details from api."""
    moz_results = {}
    # backlinks
    # api = 'http://lsapi.seomoz.com/linkscape/links/moz.com'
    # payload = {'Scope':'page_to_page',
    #             'AccessID': 'mozscape-c65de9bb80',
    #             'Expires': '1541241748',
    #             'Signature': create_signature('mozscape-c65de9bb80',
    #                       1541241748, '7bae6c85efc211bf84d09f001a488608'),
    #             'Sort': 'page_authority',
    #             'Filter':'internal+301',
    #             'Limit':'1',
    #             'SourceCols':'536870916',
    #             'TargetCols':'4',
    #             }

    api = 'http://lsapi.seomoz.com/linkscape/url-metrics/' + url
    payload = {'AccessID': 'mozscape-c65de9bb80',
               'Expires': '1541241748',
               'Signature':
               create_signature('mozscape-c65de9bb80', 1541241748,
                                '7bae6c85efc211bf84d09f001a488608'),
               'Cols': str(1 + 4 + 16384 + 34359738368 +
                           68719476736 + 144115188075855872),
               }

    r = requests.get(api, params=payload)
    moz_dict = json.loads((r.content).decode("utf-8"))

    try:
        moz_results['moz_rank_normalized'] = moz_dict['umrp']
        moz_results['moz_rank_raw'] = moz_dict['umrr']
        moz_results['page_authority'] = moz_dict['upa']
        moz_results['domain_authority'] = moz_dict['pda']
    except:
        pass

    return moz_results


def create_signature(access_id, expires, secret_key):
    """Signature Creation."""
    to_sign = '%s\n%i' % (access_id, expires)
    return base64.b64encode(
        hmac.new(
            secret_key.encode('utf-8'),
            to_sign.encode('utf-8'),
            hashlib.sha1).digest())

# GET ECOMMERCE PLATFORM ##############################

# def get_ecommerce_site(url):
#     """
#     Quick and easy solution: Use Builtwith api(but it is a paid resource)
#     Another way is to traverse the whole page and start looking for keywords
#     such as shopify and magento in it. Since
#     mostly all these platforms have their names present in the source code
#     somewhere. There are exceptions to that as well
#     for eg Word press hides itself if we use a plugin.
#     """
#     # r = requests.get('http://builtwith.com/'+url)
#     # soup = BeautifulSoup(r1.content, 'html5lib')
#     # print(soup.body.findAll(text=re.compile('^shopify$')))
#     # print(builtwith.parse(url))
