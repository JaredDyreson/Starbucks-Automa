# Documentation

## addingEvents

This module is specifically aimed to handle all requests to and from the Google API. Most calls need a JSON body as a form of input which is seen in the `get_free_busy` function.

## GoogleEventHandler [Class]

GoogleEventHandler has two distinct attributes:

- Credentials: calls gen_credentials to return proper authentication to make calls to the Google Calendar API
- Service Handler: this uses such credentials to create a service to send and receive requests.

### gen_credentials [Function]

Here we are using a hard-coded location to where our credentials are stored. The convenient part of the Google Calendar API is that authentication can be achieved through the use of `token.pickle` files. These never expire and can be continually used. It is auto generated when the user is setting up a new project to work with the Google Calendar API (GCA). The trade-off, however, is that since it does not require any further authentication, malicious code execution can be easily achieved. This is why in the future the script should be run as root along with read only capabilities by root. Also, at the moment we are using JSON to store the username and password for the site we which to reach. The next major step is to move the JSON data and subsequently depreciate `JSONParser.py` into a database. It should also be know that this and all other functions in this header have the capability to be recycled into other codebases. This function was directly pulled from [here](https://developers.google.com/calendar/quickstart/python) and this section also contains more documentation on how to get your `token.pickle` file.

## add_event



```python
print("Hello World")
```

# External Links

- [Calculendar](https://github.com/mattmight/calculendar/blob/a4e9b4e651851d44aa50da686e4a2bc89d5b4452/gcal.py)
