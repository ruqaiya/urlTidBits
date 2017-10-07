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


# Create your views here.

def home(request):
    context = {}

    if request.method == 'POST':
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
        
        # get_ecommerce_site(request.POST['url'])

        context.update({
            'metaTags': metaTags,
            'alexarank': alexarank,
            'companyInfo': address_data,
            'socialmedia': social_media_handles,
            'admincontact': admin_contact,
            'ip':ip,
            'response': True,
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
        soup = BeautifulSoup(response.content, "html.parser")

        metas = soup.find_all('meta')

        metaTagContent={}
        for meta in metas:
            if 'name' in meta.attrs:
                metaTagContent[meta.attrs['name']]=meta.attrs['content']
                       
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

############### GET ECOMMERCE PLATFORM ##############################

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