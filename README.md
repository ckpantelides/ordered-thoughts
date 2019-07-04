Ordered thoughts
=================

It's hosted [here](http://orderedthoughts.herokuapp.com)

A python app built with flask. It stores your thoughts by category for easy recall (in a SQL database).

I created the user authentication for multiple users, and used werkzeug to salt and hash the login details.

![img1]

![img2]

![img3]

[img1]: https://github.com/ckpantelides/airport/blob/master/airport1.PNG
[img2]: https://github.com/ckpantelides/airport/blob/master/airport2.PNG
[img3]: https://github.com/ckpantelides/airport/blob/master/airport3.PNG

#### Installation

> pip install flask, flask-session and psycopg2

> python hello.py

> (A local database will need to be implemented; it currently connects to the hosted postgresql database)
