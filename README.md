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

1) writing unit tests
2) Functionalities:
	1) Cater Urls in all format. Not only the specific method defined.
	2) Cater HTTPS urls as well.
	3) If a social media page is entered like facebook.com, the social media handles functionality breaks. I would have liked to fix that.
3) Make the UI much better.

## Notes

The following URLS are tested: 'taxals.com', 'google.com', 'facebook.com'
Please be very speciifc to the url format you enter.

Note: Please only enter sites with http scheme and not https scheme. It will not work for https.

Note: The only format that will work is 'www.example.com'. Please write the complete domain of the site.

    The version that will work:
    www.example.com

    The versions that will not work:
    http://www.example.com
    example
    www.example
