Ordered thoughts
=================

It's hosted [here](http://orderedthoughts.herokuapp.com)

A python app built with flask.

#### Store your thoughts by category for easy recall

I created the user authentication, using the werkzeug package to salt and hash login details. Flask-session ensures the user needs to be logged in to view the routes to add new thoughts etc. It's currently hosted on heroku, with a postgresql database to store the data in relational tables.

![img1]

![img2]

![img3]

[img1]: https://github.com/ckpantelides/ordered-thoughts/blob/images/ordered-crop1.jpg
[img2]: https://github.com/ckpantelides/ordered-thoughts/blob/images/ordered-crop2.jpg
[img3]: https://github.com/ckpantelides/ordered-thoughts/blob/images/ordered-crop3.jpg

#### Installation

> pip install flask, flask-session and psycopg2

> python hello.py

> (A local database will need to be staged; it currently connects to the hosted postgresql database)
