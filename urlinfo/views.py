from django.shortcuts import redirect, render, render_to_response
from django.template import RequestContext

from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests

# import seolib as seo
import whois

import re
import json

import socket

from geopy.geocoders import Nominatim

import re
import http.client

from builtwith import BuiltWith



# import httplib


# Create your views here.

def home(request):
    context = {}

    if request.method == 'POST':
        ip = get_ip(request.POST['url'])
        url_ip = 'http://'+ip
        url = 'http://'+request.POST['url']
        
        metaTags = get_meta_tags(url_ip)
        alexarank = alexa_rank(request.POST['url'])

        admin_contact = get_admin_contact(url)

        address_data = get_address(ip)
        
        social_media_handles = get_social_media_handles(url_ip)
        
        # get_ecommerce_site(request.POST['url'])

        context.update({
            'metaTags': metaTags,
            'alexarank': alexarank,
            'companyInfo': address_data,
            'socialmedia': social_media_handles,
            'admincontact': admin_contact,
        })
    else:
        pass

    return render(request, 'home.html', context)


def get_meta_tags(ip):
    response = requests.get(ip)
    soup = BeautifulSoup(response.content, "html.parser")

    metas = soup.find_all('meta')

    metaTagContent={}
    for meta in metas:
        if 'name' in meta.attrs:
            metaTagContent[meta.attrs['name']]=meta.attrs['content']
                   
    return metaTagContent

def alexa_rank(url):
    """
    Parsing XML from data.alexa.com
    and taking alexa rank out of it.
    """
    alexa_rank_url = "http://data.alexa.com/data?cli=10&dat=s&url="+ url
    r = requests.get(alexa_rank_url)
    bs = None
    
    try:
        bs = BeautifulSoup(r.content, "xml").find("REACH")['RANK']
    except:
        pass

    return bs

def get_admin_contact(url):    
    """
    At the moment I am simply calling whois library to get contact name and email(some times given).

    Ideally wanted to traverse https://www.whois.com/whois/
    for this information since whois library does not return the whole information.
    Since I did not have time to setup my python environment for ssl so I couldn't traverse https site.
    That would have given me a phone number as well. 
    """
    w = whois.whois(url)
    data = {}
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

    return data


def get_address(ip):
    url = 'https://ipinfo.io/'+ip+'/json'
    r = requests.get(url)
    data = json.loads(r.content.decode('utf-8'))

    location = data['loc']
    geolocator = Nominatim()
    location = geolocator.reverse(location)
    data['address'] = location.address

    FREEGEOPIP_URL = 'http://freegeoip.net/json'
    url = '{}/{}'.format(FREEGEOPIP_URL, ip)
    response = requests.get(url)
    response_data = response.json()
    data['timezone'] = response_data['time_zone']

    return data

def get_ip(url):
    ip = get_ips_for_host(url)
    
    try:
        return(ip[2][0])
    except:
        print('couldn\'t get ip')

    return None

def get_ips_for_host(host):
    try:
        ips = socket.gethostbyname_ex(host)
    except socket.gaierror:
        ips=[]
    return ips

def get_social_media_handles(url):
    """
    TO-DO: need to ignore the main site if the url is of the same social site.
    For eg if the url to test is Facebook.com we need to remove facebook.com from
    sm_sites list.
    """
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

# def get_ecommerce_site(url):
#     """
#     Quick and easy solution: Use Builtwith API(but it is a paid resource) 
#     Another way is to traverse the whole page and start looking for keywords such as shopify and magento in it. Since
#     mostly all these platforms have their names present in the source code. There are exceptions to that as well for eg
#     Word press hides itself if we use a plugin. 
#     """
#     # r = requests.get('http://builtwith.com/'+url)
#     # soup = BeautifulSoup(r1.content, 'html5lib')
#     # print(soup.body.findAll(text=re.compile('^shopify$')))
#     # print(builtwith.parse(url)) 