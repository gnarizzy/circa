# Circa
## Buy and Sell Locally

Circa is a platform for local buying and selling. It creates a hassle-free experience by handling payments, delivery, and returns Cheaper than Amazon, safer than Craigslist.

Circa was originally created by [Gautam Narula](https://github.com/gnarizzy) and [Andrew Schuster](https://github.com/aschuster3), co-founders (and Chief Donut Procurer and Chief Delivery Boy, respectively) of Centaurii, Inc. Now that Centaurii is defunct, Gautam (me) has open-sourced the code and am the sole maintainer. I am currently working on [Circa 2.0](http://www.usecirca.com/circa2/), a ground-up rewriting of the codebase that will turn Circa into an automated, self-service platform. Until it is launched, Circa will remain in [test mode](http://www.usecirca.com/test/) at www.usecirca.com.

To run your own instance of Circa, do the following:

1. Clone this repo and install [Pip](https://pypi.python.org/pypi/pip) if you don't already have it. 
2. Use your terminal to navigate to the directory with requirements.txt and run `pip install -r requirements.txt`. This will install all the necessary packages to run Circa. 
3. You will need to a Django settings file with all the appropriate packages included in `INSTALLED_APPS`. Copy this ['settings.py' file](https://gist.github.com/gnarizzy/961a63063f16b3b9c9f5dacc8c8e42df) into the circa subdirectory (the one containing urls.py), and generate your own secret key. You will also have to change `ALLOWED_HOSTS` and `SITE_DOMAIN` to the appropriate values if you plan on running this in production. 
4. You will need to create a file called 'keys.py', which will require your Stripe API keys to process real or test payments. Copy [this keys.py file](https://gist.github.com/gnarizzy/d4d56af25f354214d90f7712d537ffa9) into the 'core' directory and set your API keys accordingly. You can get these API keys by creating a Stripe account and following their instructions.
5. You will need to create a database and migrations. Navigating to the directory with manage.py and running `python manage.py migrate` should take care of that. If you'd like to use a database other than the default sqlite3, you'll have to do additional configuration. 
6. Run 'python manage.py runserver' to run a local instance of Circa. That's it! Please note that Circa is not compatible with Python 2.x. 

##Notes##

1. When `debug=true` in settings.py, the site goes into test mode and the test Stripe API keys are automatically used instead of the live ones. Look at the Stripe documentation for test mode to see how to simulate credit card transactions. 
2. If you plan on doing real credit card transactions, **make sure you have SSL (HTTPS) enabled on your site!** Not doing so means your users credit card information will be sent unencrypted over the interwebz.
3. This repo will no longer be updated, since it is being superceded by Circa 2.0, which will be in a separate repo. 
4. This code is licensed under the MIT license. If you do something cool with it, I'd love to hear about it! 
5. The `EMAIL_BACKEND` and `DEFAULT_FROM_EMAIL` will have to be updated accordingly. Also, Mandrill doesn't really work the way it did when we were using it for Circa, so keep that in mind. 
