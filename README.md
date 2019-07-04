Ordered thoughts
=================

It's hosted [here](http://orderedthoughts.herokuapp.com)

A python app built with flask. It stores your thoughts by category for easy recall (in a SQL database).

I created the user authentication, and used the werkzeug package to salt and hash the login details.

![img1]

![img2]

![img3]

[img1]: https://github.com/ckpantelides/ordered-thoughts/blob/images/ordered-crop1.jpg
[img2]: https://github.com/ckpantelides/ordered-thoughts/blob/images/ordered2.jpg
[img3]: https://github.com/ckpantelides/ordered-thoughts/blob/images/ordered3.jpg

#### Installation

> pip install flask, flask-session and psycopg2

> python hello.py

> (A local database will need to be staged; it currently connects to the hosted postgresql database)
