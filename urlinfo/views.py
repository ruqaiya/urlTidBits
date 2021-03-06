from django.shortcuts import redirect, render, render_to_response
from django.template import RequestContext
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import whois

import re
import json
import socket
import re
import http.client
from geopy.geocoders import Nominatim
from builtwith import BuiltWith

import codecs
import hashlib
import hmac
import time
import base64

# Create your views here.

def home(request):
    context = {}

    if request.method == 'POST':
        raw_url = request.POST['url']
        try:
            ip = get_ip(request.POST['url'])
        except:
            ip = None

        if ip is not None:
            url_ip = 'http://'+ip
            metaTags = get_meta_tags(url_ip)
            address_data = get_address(ip)
            social_media_handles = get_social_media_handles(url_ip)
        else:
            ip = 'error'
            metaTags = None
            address_data = None
            social_media_handles = None
        
        url = 'http://'+request.POST['url']
        admin_contact = get_admin_contact(url)

        alexarank = alexa_rank(request.POST['url'])

        ### testing MOZ API

        try:
            moz_results = get_moz_details(request.POST['url'])
        except:
            moz_results = {}
            print('moz did not work')
        
        # get_ecommerce_site(request.POST['url'])

        context.update({
            'metaTags': metaTags,
            'alexarank': alexarank,
            'companyInfo': address_data,
            'socialmedia': social_media_handles,
            'admincontact': admin_contact,
            'ip':ip,
            'response': True,
            'raw_url': raw_url,
            'moz_results': moz_results,
        })
    else:
        pass

    return render(request, 'home.html', context)


def get_meta_tags(ip):
    """
    Getting meta tags by scraping through the page and looking for the particular tags.
    """

    try:
        response = requests.get(ip)
        # print(response.content)
        soup = BeautifulSoup(response.content, "html.parser")
        # print(soup)
        metas = soup.find_all('meta')

        # print(metas)
        metaTagContent={}
        for meta in metas:
            if 'name' in meta.attrs:
                metaTagContent[meta.attrs['name']]=meta.attrs['content']

        response = requests.get(ip)
        soup = BeautifulSoup(response.content, "html.parser")

        title_tag = soup.find_all('title')

        # print(title_tag)

        for title in title_tag:
            title_text = title.text
            metaTagContent['title'] = title_text
                       
        return metaTagContent
    except:
        return None

def alexa_rank(url):
    """
    Parsing XML from data.alexa.com
    and taking alexa rank out of it.
    """
    try:
        alexa_rank_url = "http://data.alexa.com/data?cli=10&dat=s&url="+ url
        r = requests.get(alexa_rank_url)
    except:
        bs = None
    
    try:
        bs = BeautifulSoup(r.content, "xml").find("REACH")['RANK']
    except:
        bs = 'No rank is available for this site.'

    return bs

def get_admin_contact(url):    
    """
    At the moment I am simply calling whois library to get contact name and email(some times given).

    Ideally wanted to traverse https://www.whois.com/whois/
    for this information since whois library does not return the whole information.
    Since I did not have time to setup my python environment for ssl so I couldn't traverse https site.
    That would have given me a phone number as well. 
    """
    data = {}

    try:
        w = whois.whois(url)
    except:
        pass
    
    try:
        data['name'] = w['name']        # adding each data element in a seperate try/catch so nothing is missed and all data that is available is extracted.
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

    return data

###### GET CONTACT DETAILS + STREET ADDRESS + TIMEZONE ##########################

def get_address(ip):
    try:
        url = 'https://ipinfo.io/'+ip+'/json'                   # getting Country, co-ordinates and street address from ipinfo
        r = requests.get(url)
        data = json.loads(r.content.decode('utf-8'))

        location = data['loc']
        geolocator = Nominatim()
        location = geolocator.reverse(location)
        data['address'] = location.address
    except:
        data = {}

    try:
        FREEGEOPIP_URL = 'http://freegeoip.net/json'            # getting timezone from geoip
        url = '{}/{}'.format(FREEGEOPIP_URL, ip)
        response = requests.get(url)
        response_data = response.json()
        data['timezone'] = response_data['time_zone']
    except:
        pass

    return data

################### GET IP FROM URL ######################

def get_ip(url):    
    try:
        ip = get_ips_for_host(url)
        return(ip[2][0])
    except:
        ip = None

    return ip

def get_ips_for_host(host):
    try:
        ips = socket.gethostbyname_ex(host)
    except socket.gaierror:
        ips=[]
    return ips

############### GET SOCIAL MEDIA HANDLES ##############################

def get_social_media_handles(url):
    """
    TO-DO: need to ignore the main site if the url is of the same social site.
    For eg if the url to test is Facebook.com we need to remove facebook.com from
    sm_sites list.
    """
    try:
        r = requests.get(url)
        sm_sites = ['twitter.com','facebook.com', 'plus.google.com', 'pinterest.com', 'instagram.com']
        sm_sites_present = []

        soup = BeautifulSoup(r.content, 'html5lib')
        all_links = soup.find_all('a', href = True)

        for sm_site in sm_sites:
            for link in all_links:
                if sm_site in link.attrs['href']:
                    sm_sites_present.append(link.attrs['href'])

        return sm_sites_present
    except:
        return None

def get_moz_details(url):
    moz_results={}
    ### backlinks
    # API = 'http://lsapi.seomoz.com/linkscape/links/moz.com'
    # payload = {'Scope':'page_to_page',
    #             'AccessID': 'mozscape-c65de9bb80',
    #             'Expires': '1541241748',
    #             'Signature': create_signature('mozscape-c65de9bb80', 1541241748, '7bae6c85efc211bf84d09f001a488608'),
    #             'Sort': 'page_authority',
    #             'Filter':'internal+301',
    #             'Limit':'1',
    #             'SourceCols':'536870916',
    #             'TargetCols':'4',
    #             }

    API = 'http://lsapi.seomoz.com/linkscape/url-metrics/'+url
    payload = {'AccessID': 'mozscape-c65de9bb80',
                'Expires': '1541241748',
                'Signature': create_signature('mozscape-c65de9bb80', 1541241748, '7bae6c85efc211bf84d09f001a488608'),
                'Cols':str(1+4+16384+34359738368+68719476736+144115188075855872),
                }    

    r = requests.get(API, params=payload)
    moz_dict=json.loads((r.content).decode("utf-8"))

    try:
        moz_results['moz_rank_normalized'] = moz_dict['umrp']
        moz_results['moz_rank_raw'] = moz_dict['umrr']
        moz_results['page_authority'] = moz_dict['upa']
        moz_results['domain_authority'] = moz_dict['pda']
    except:
        pass

    return moz_results

def create_signature(access_id, expires, secret_key):
    to_sign = '%s\n%i' % (access_id, expires)
    return base64.b64encode(
        hmac.new(
            secret_key.encode('utf-8'),
            to_sign.encode('utf-8'),
            hashlib.sha1).digest())

############### GET ECOMMERCE PLATFORM ##############################

# def get_ecommerce_site(url):
#     """
#     Quick and easy solution: Use Builtwith API(but it is a paid resource) 
#     Another way is to traverse the whole page and start looking for keywords such as shopify and magento in it. Since
#     mostly all these platforms have their names present in the source code somewhere. There are exceptions to that as well
#     for eg Word press hides itself if we use a plugin. 
#     """
#     # r = requests.get('http://builtwith.com/'+url)
#     # soup = BeautifulSoup(r1.content, 'html5lib')
#     # print(soup.body.findAll(text=re.compile('^shopify$')))
#     # print(builtwith.parse(url)) 