# urlTidBits
Hubba - Senior Python Developer - Technical Project

## Setup

1) This project is using Python 3.4. Make a virtual environment.

```
virtualenv urlTidBitsENV
```

2) Clone the project into your local directory.
3) From inside the directory run the requirements.txt file.

```
pip install -r requirements.txt
```

4) You're all setup! Just run the project.

```
python manage.py runserver
```

## Things to do

Since I didn't have time at all during the week to work on the project in detail' please find the following list without which I wouldn't like to commit my work.

1) figure out ecommerce platform of the given url.
2) writing unit tests
3) Functionalities:
	1) Cater Urls in all format. Not only the specific method defined.
	2) If a social media page is entered like facebook.com, the social media handles functionality breaks. I would have liked to fix that.
4) Make the UI much better.
5) Test the system on all browsers, for more domains and IPS and document its limitations.

## Notes

### Testing

The following URLS are tested: 'taxals.com', 'google.com', 'facebook.com'
The site is tested only on firefox and Chrome.

### Input Format
Please be very speciifc to the url format you enter.

Note: The only format that will work is 'www.example.com' or 'example.com'. Please write the complete domain of the site.

    The version that will work:
    www.example.com
    example.com

    The versions that will not work:
    http://www.example.com
    example
    www.example

### Limitations
Any website having different IPs for their domains with www and without www would get meta tags and title tag information for only the IP that we have entered and the IP the site is being redirected to. For eg www.hubba.com is redirected to hubba.com. The tag information is correct only for hubba.com and not for www.hubba.com

Also the Social Media section will not work properly for the following sites:
'twitter.com','facebook.com', 'plus.google.com', 'pinterest.com', 'instagram.com'
