# Flask problems, debugging and solution
Sat Mar 09 2024

## User in UI does not persist
Mon Mar 11 2024

- Token based auth 
  - https://realpython.com/token-based-authentication-with-flask/

- Bearer vs Cookies
  - https://stackoverflow.com/questions/37582444/jwt-vs-cookies-for-token-based-authentication
    - Bearer ttoken has to be sent by the browser code explicitly
	- cookies are always sent
  
``` text
The biggest difference between bearer tokens and cookies is that the browser will automatically send cookies, where bearer tokens need to be added explicitly to the HTTP request.

This feature makes cookies a good way to secure websites, where a user logs in and navigates between pages using links.

The browser automatically sending cookies also has a big downside, which is CSRF attacks. In a CSRF attack, a malicious website takes advantage of the fact that your browser will automatically attach authentication cookies to requests to that domain and tricks your browser into executing a request.

Suppose the web site at https://www.example.com allows authenticated users to change their passwords by POST-ing the new password to https://www.example.com/changepassword without requiring the username or old password to be posted.

If you are still logged in to that website when you visit a malicious website which loads a page in your browser that triggers a POST to that address, your browser will faithfully attach the authentication cookies, allowing the attacker to change your password.

Cookies can also be used to protect web services, but nowadays bearer tokens are used most often. If you use cookies to protect your web service, that service needs to live on the domain for which the authentication cookies are set, as the same-origin policy won't send cookies to another domain.

Also, cookies make it more difficult for non-browser based applications (like mobile to tablet apps) to consume your API.
```

- more info 

``` text
Overview

What you're asking for is the difference between cookies and bearer tokens for sending JSON Web Tokens (JWTs) from the client to the server.

Both cookies and bearer tokens send data.

One difference is that cookies are for sending and storing arbitrary data, whereas bearer tokens are specifically for sending authorization data.

That data is often encoded as a JWT.
Cookie

A cookie is a name-value pair, that is stored in a web browser, and that has an expiry date and associated domain.

We store cookies in a web browser either with JavaScript or with an HTTP Response header.

document.cookie = 'my_cookie_name=my_cookie_value'   // JavaScript
Set-Cookie: my_cookie_name=my_cookie_value           // HTTP Response Header

The web browser automatically sends cookies with every request to the cookie's domain.

GET http://www.bigfont.ca
Cookie: my_cookie_name=my_cookie_value               // HTTP Request Header

Bearer Token

A bearer token is a value that goes into the Authorization header of any HTTP Request. It is not automatically stored anywhere, it has no expiry date, and no associated domain. It's just a value. We manually store that value in our clients and manually add that value to the HTTP Authorization header.

GET http://www.bigfont.ca
Authorization: Bearer my_bearer_token_value          // HTTP Request Header

JWT and Token Based Authentication

When we do token-based authentication, such as OpenID, OAuth, or OpenID Connect, we receive an access_token (and sometimes id_token) from a trusted authority. Usually we want to store it and send it along with HTTP Requests for protected resources. How do we do that?

Option 1 is to store the token(s) in a cookie. This handles storage and also automatically sends the token(s) to the server in the Cookie header of each request. The server then parses the cookie, checks the token(s), and responds accordingly.

Option 2 is to store the token in local/session storage, and then manually set the Authorization header of each request. In this case, the server reads the header and proceeds just like with a cookie.

It's worth reading the linked RFCs to learn more.

```

## TypeError: Object of type Date is not JSON serializable
Mon Mar 11 2024

- some data from db are returned as Neo4j.time.Date objects in output
  - eg born, died etc for actor/director data
- jsonify cannot handle these types of data

- but using jsonify is reccomended 
  - it properly handles http response and adds info for javascript
  
- solutions:
  - preprocess json data:
    - first convert data to str using json.dumps and json.loads
	- 
    - then use jsonify
  - modify behavior of jsonify

- serializing datetime
  - https://stackoverflow.com/questions/11875770/how-can-i-overcome-datetime-datetime-not-json-serializable
  - https://stackoverflow.com/questions/61074324/how-to-fix-python-at-object-of-type-datetime-is-not-json-serializable-error
  - 
  
- Flask jsonify notes
  - https://stackoverflow.com/questions/43663552/keep-a-datetime-date-in-yyyy-mm-dd-format-when-using-flasks-jsonify
    - uses json encoder class
	- converts dates to isoformat - more portable
  - https://flask.palletsprojects.com/en/2.3.x/api/#flask.json.jsonify
  - https://flask.palletsprojects.com/en/2.3.x/api/#flask.json.provider.JSONProvider
  
``` python
Flask uses Python’s built-in json module for handling JSON by default. The JSON implementation can be changed by assigning a different provider to flask.Flask.json_provider_class or flask.Flask.json. The functions provided by flask.json will use methods on app.json if an app context is active.
```
    - app.json_provider_class: is the class which handles json
	  - default is:  class DefaultJSONProvider(JSONProvider) in  flask/src/flask/json/provider.py
	    - https://github.com/pallets/flask/blob/a6007373b5c521297e2ec24f820b9c7c32659af8/src/flask/json/provider.py#L123C1-L123C41
	  - defined in: app.py
	  - can be user supplied class
	- https://docs.python.org/3/library/json.html
	  - used by  DefaultJSONProvider
	  - using a custom default method passed to json.dumps to handle non string objects

``` python
 json.dumps(obj, *, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=None, default=None, sort_keys=False, **kw)
```
    - app.json: an instance of  app.json_provider_class
	  - used to jsonify
	  - can be user supplied instance of the class
	 
  - https://github.com/pallets/flask/pull/4692#issue-1303581666
    - example of using JSONProvider
	
``` python
from flask.json.provider import JSONProvider
import orjson

class OrJSONProvider(JSONProvider):
    def dumps(self, obj, *, option=None, **kwargs):
        if option is None:
            option = orjson.OPT_APPEND_NEWLINE | orjson.OPT_NAIVE_UTC
        
        return orjson.dumps(obj, option=option).decode()

    def loads(self, s, **kwargs):
        return orjson.loads(s)

# assign to an app instance
app.json = OrJSONProvider(app)

# or assign in a subclass
class MyFlask(Flask):
    json_provider_class = OrJSONProvider

app = MyFlask(__name__)
```

- api/utils/json.py contains two methods
  - stringify_json
    - uses dumps and loads to create a str version of json
	- eg in routes/movies.py in get_movie_details(movie_id)
	  - movie = stringify_json(movie)
	- call it before running jsonify
	- works

  - NeoJsonProvider class
    - checks for neo4j.time.Date and converts to isoformat
    - in app set: app.json = NeoJsonProvider(app)
	- works
  
## JWT auth/token error
Sat Mar 09 2024

- Summary:
  - code used to debug
  
``` python
from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity

print request details for debugging
current_app.logger.debug("get_movies")
current_app.logger.debug("Request Args %s", request.args)
current_app.logger.debug("Request Headers %s", request.headers)
current_app.logger.debug("JWT %s", get_jwt())
current_app.logger.debug("JWT identity %s", get_jwt_identity())
current_app.logger.debug("current user %s", current_user)
```

- inspecting request headers and other info in request object
  - https://stackoverflow.com/questions/29386995/how-to-get-http-headers-in-flask
  - https://stackoverflow.com/questions/25466904/print-raw-http-request-in-flask-or-wsgi
    - using middleware to log requests
	
  - https://stackoverflow.com/questions/14047393/flask-request-debugging
  - https://stackoverflow.com/questions/36076490/debugging-a-request-response-in-python-flask
    - using after-request and before-request to inspect response and request payloads
	
  - https://pypi.org/project/Flask-DebugToolbar/
    - this is add-on to enable debugging 
	
  - https://bobbyhadz.com/blog/how-to-get-http-headers-in-flask
  
- added some debug statements in api/routes/movies.py in get_movies
  - print(request.headers)
    - works and lists the header info one per line
	
```
Host: localhost:3000
User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0
Accept: application/json, text/plain, */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: http://localhost:3000/
Connection: keep-alive
Cookie: tj_auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uSWQiOiJlODEwMTQwMi0wMDZkLTQ4MmEtYmM1YS0wNTZkMGU5NmE0MDgiLCJ1c2VybmFtZSI6ImNhNTQ2NDEzLTEwODgtNGY5OC1iMTIxLWViNjgxNzMzYjA3ZiIsInN1YiI6InBrbkBwa25hbmRpdGEubmV0Iiwib3JnYW5pemF0aW9uSWRzIjpbImFmOTBjNWZiLWVlYWQtNDFmNS05ZjBiLWM5ZGRkMzdiYzFkOCJdLCJpc1NTT0xvZ2luIjpmYWxzZSwiaXNQYXNzd29yZExvZ2luIjp0cnVlLCJpYXQiOjE3MDY2NDE3OTF9.ki8E8xqnOKTTq4byMa7A7Z6NzMNjMxg4cG76tt5SYcY
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
```

  - pprint.pformat does not work at all
  
  - pprint.pprint works but produces a different format
  
```
EnvironHeaders([('Host', 'localhost:3000'), ('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0'), ('Accept', 'application/json, text/plain, */*'), ('Accept-Language', 'en-US,en;q=0.5'), ('Accept-Encoding', 'gzip, deflate, br'), ('Referer', 'http://localhost:3000/'), ('Connection', 'keep-alive'), ('Cookie', 'tj_auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uSWQiOiJlODEwMTQwMi0wMDZkLTQ4MmEtYmM1YS0wNTZkMGU5NmE0MDgiLCJ1c2VybmFtZSI6ImNhNTQ2NDEzLTEwODgtNGY5OC1iMTIxLWViNjgxNzMzYjA3ZiIsInN1YiI6InBrbkBwa25hbmRpdGEubmV0Iiwib3JnYW5pemF0aW9uSWRzIjpbImFmOTBjNWZiLWVlYWQtNDFmNS05ZjBiLWM5ZGRkMzdiYzFkOCJdLCJpc1NTT0xvZ2luIjpmYWxzZSwiaXNQYXNzd29yZExvZ2luIjp0cnVlLCJpYXQiOjE3MDY2NDE3OTF9.ki8E8xqnOKTTq4byMa7A7Z6NzMNjMxg4cG76tt5SYcY'), ('Sec-Fetch-Dest', 'empty'), ('Sec-Fetch-Mode', 'cors'), ('Sec-Fetch-Site', 'same-origin')])
```
  
  - current_app.logger.debug("Request Headers %s", request.headers)
    - unlike the previous ones this prints in order of request
	- the others may print out of order

  - final debug statements in api/routes
    - movies.py: get_movies
	- auth.py: register, login
  
```
    # print request details
    current_app.logger.debug("get_movies")
    current_app.logger.debug("Request Args %s", request.args)
    current_app.logger.debug("Request Headers %s", request.headers)
```

- info from debug logs
  - first login is requested, ends in success
  - then get_movies is requested twice once for released, one for imdbRating sorted
  - for both a Authorization: Bearer with token is sent with request
  - then for both error is thrown - info later

```
[2024-03-09 11:37:44,380] DEBUG in auth: login
[2024-03-09 11:37:44,380] DEBUG in auth: Request Args ImmutableMultiDict([])
[2024-03-09 11:37:44,381] DEBUG in auth: Request Headers Host: localhost:3000
User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0
Accept: application/json, text/plain, */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Content-Type: application/json
Content-Length: 43
Origin: http://localhost:3000
Connection: keep-alive
Referer: http://localhost:3000/login
Cookie: tj_auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uSWQiOiJlODEwMTQwMi0wMDZkLTQ4MmEtYmM1YS0wNTZkMGU5NmE0MDgiLCJ1c2VybmFtZSI6ImNhNTQ2NDEzLTEwODgtNGY5OC1iMTIxLWViNjgxNzMzYjA3ZiIsInN1YiI6InBrbkBwa25hbmRpdGEubmV0Iiwib3JnYW5pemF0aW9uSWRzIjpbImFmOTBjNWZiLWVlYWQtNDFmNS05ZjBiLWM5ZGRkMzdiYzFkOCJdLCJpc1NTT0xvZ2luIjpmYWxzZSwiaXNQYXNzd29yZExvZ2luIjp0cnVlLCJpYXQiOjE3MDY2NDE3OTF9.ki8E8xqnOKTTq4byMa7A7Z6NzMNjMxg4cG76tt5SYcY
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin


127.0.0.1 - - [09/Mar/2024 11:37:44] "POST /api/auth/login HTTP/1.1" 200 -
[2024-03-09 11:37:44,865] DEBUG in movies: get_movies
[2024-03-09 11:37:44,865] DEBUG in movies: Request Args ImmutableMultiDict([('sort', 'imdbRating'), ('order', 'desc'), ('limit', '6'), ('limit', '6')])
[2024-03-09 11:37:44,866] DEBUG in movies: Request Headers Host: localhost:3000
User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJlODdkNDkzOC04YTRjLTQ2MjEtODk4OS03NzNkYzA1Zjg5MzAiLCJlbWFpbCI6Im1tbUBtbW0uY29tIiwibmFtZSI6Ik1NTSBjb20iLCJzdWIiOiJlODdkNDkzOC04YTRjLTQ2MjEtODk4OS03NzNkYzA1Zjg5MzAiLCJpYXQiOjE3MTAwMDIyNjQsIm5iZiI6MTcxMDAwMjI2NCwiZXhwIjoxNzQxMTA2MjY0fQ.huLq2TSofh8wORMO5e6bhxpJZ3_tHFyOEAib3SsOBDE
Referer: http://localhost:3000/
Connection: keep-alive
Cookie: tj_auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uSWQiOiJlODEwMTQwMi0wMDZkLTQ4MmEtYmM1YS0wNTZkMGU5NmE0MDgiLCJ1c2VybmFtZSI6ImNhNTQ2NDEzLTEwODgtNGY5OC1iMTIxLWViNjgxNzMzYjA3ZiIsInN1YiI6InBrbkBwa25hbmRpdGEubmV0Iiwib3JnYW5pemF0aW9uSWRzIjpbImFmOTBjNWZiLWVlYWQtNDFmNS05ZjBiLWM5ZGRkMzdiYzFkOCJdLCJpc1NTT0xvZ2luIjpmYWxzZSwiaXNQYXNzd29yZExvZ2luIjp0cnVlLCJpYXQiOjE3MDY2NDE3OTF9.ki8E8xqnOKTTq4byMa7A7Z6NzMNjMxg4cG76tt5SYcY
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin


[2024-03-09 11:37:44,867] DEBUG in movies: get_movies
[2024-03-09 11:37:44,869] DEBUG in movies: Request Args ImmutableMultiDict([('sort', 'released'), ('order', 'desc'), ('limit', '6'), ('limit', '6')])
[2024-03-09 11:37:44,869] DEBUG in movies: Request Headers Host: localhost:3000
User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJlODdkNDkzOC04YTRjLTQ2MjEtODk4OS03NzNkYzA1Zjg5MzAiLCJlbWFpbCI6Im1tbUBtbW0uY29tIiwibmFtZSI6Ik1NTSBjb20iLCJzdWIiOiJlODdkNDkzOC04YTRjLTQ2MjEtODk4OS03NzNkYzA1Zjg5MzAiLCJpYXQiOjE3MTAwMDIyNjQsIm5iZiI6MTcxMDAwMjI2NCwiZXhwIjoxNzQxMTA2MjY0fQ.huLq2TSofh8wORMO5e6bhxpJZ3_tHFyOEAib3SsOBDE
Referer: http://localhost:3000/
Connection: keep-alive
Cookie: tj_auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXNzaW9uSWQiOiJlODEwMTQwMi0wMDZkLTQ4MmEtYmM1YS0wNTZkMGU5NmE0MDgiLCJ1c2VybmFtZSI6ImNhNTQ2NDEzLTEwODgtNGY5OC1iMTIxLWViNjgxNzMzYjA3ZiIsInN1YiI6InBrbkBwa25hbmRpdGEubmV0Iiwib3JnYW5pemF0aW9uSWRzIjpbImFmOTBjNWZiLWVlYWQtNDFmNS05ZjBiLWM5ZGRkMzdiYzFkOCJdLCJpc1NTT0xvZ2luIjpmYWxzZSwiaXNQYXNzd29yZExvZ2luIjp0cnVlLCJpYXQiOjE3MDY2NDE3OTF9.ki8E8xqnOKTTq4byMa7A7Z6NzMNjMxg4cG76tt5SYcY
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
```

- error message (stripped)

```
  File "/home/DEV/Neo4j-Proj/ga-app-python/api/routes/movies.py", line 28, in get_movies
    user_id = current_user["sub"] if current_user != None else None
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.
.
.
  File "/home/pkn/Store/Python/Anaconda/linux-conda-ilish/envs/ga-app-python/lib/python3.11/site-packages/flask_jwt_extended/utils.py", line 96, in get_current_user
    raise RuntimeError()
RuntimeError: You must provide a `@jwt.user_lookup_loader` callback to use this method
```

- docs
  - https://github.com/vimalloc/flask-jwt-extended/issues/414
    - does not solve the issue, uses @jwt.user_identity_loader
  - https://github.com/vimalloc/flask-jwt-extended/issues/408
    - does not solve the issue

  - https://codeburst.io/jwt-authorization-in-flask-c63c1acf4eeb

  - https://stackoverflow.com/questions/61116006/how-can-i-get-the-current-userid-in-flask-jwt-extended

- code documentation

  - https://flask-jwt-extended.readthedocs.io/en/stable/basic_usage.html
  - https://flask-jwt-extended.readthedocs.io/en/stable/api.html
  - https://flask-jwt-extended.readthedocs.io/en/stable/api.html#flask_jwt_extended.jwt_required
  - https://flask-jwt-extended.readthedocs.io/en/stable/automatic_user_loading.html
  
  - https://flask-jwt-extended.readthedocs.io/en/stable/automatic_user_loading.html
    - says for current_user to work need to define a callback function
    - @jwt.user_identity_loader
	- this is what the error is in the debug console
	
  - https://github.com/vimalloc/flask-jwt-extended/blob/master/examples/automatic_user_loading.py
    - code example from git source

- tutorials on flask-jwt-extended

  - https://www.youtube.com/watch?v=aX-ayOb_Aho
  - https://medium.com/pythonistas/getting-started-with-jwt-with-flask-jwt-extended-32eafe23b9bd
  - https://marketsplash.com/tutorials/flask/how-to-implement-flask-jwt-authentication/
  - https://www.geeksforgeeks.org/using-jwt-for-user-authentication-in-flask/


- added code to print jwt data in get_movies
  - from flask_jwt_extended import get_jwt
  - current_app.logger.debug("JWT %s", get_jwt())
  - after auth
  - looks good

```
[2024-03-09 14:03:31,433] DEBUG in movies: JWT {'userId': 'e87d4938-8a4c-4621-8989-773dc05f8930', 'email': 'mmm@mmm.com', 'name': 'MMM com', 'sub': 'e87d4938-8a4c-4621-8989-773dc05f8930', 'iat': 1710011011, 'nbf': 1710011011, 'exp': 1741115011, 'type': 'access', 'fresh': False, 'jti': None}
```
- added code to print jwt identity in get_movies
  - from flask_jwt_extended import get_jwt_identity
  - current_app.logger.debug("JWT identity %s", get_jwt_identity())
  - after auth
  - correct user id

```
[2024-03-09 14:20:06,656] DEBUG in movies: JWT identity e87d4938-8a4c-4621-8989-773dc05f8930
```

- automatic user loading using @jwt.user_identity_loader

``` text
# Register a callback function that takes whatever object is passed in as the
# identity when creating JWTs and converts it to a JSON serializable format.
@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


# Register a callback function that loads a user from your database whenever
# a protected route is accessed. This should return any python object on a
# successful lookup, or None if the lookup failed for any reason (for example
# if the user has been deleted from the database).
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()
```

  - one place to define these will be in create_app in api/__init__.py
  - where jwt = JWT_Manager(app) is initialized
  - but is not accessible outside
  - one way to do is to define it outside of create_app and init it in create_app
    - app factories: https://flask.palletsprojects.com/en/2.3.x/patterns/appfactories/

- quick fix in create_app in api/__init__.py
  - return jwt_data since that is what is expected in routes/movies.py

``` python
    # JWT
    jwt = JWTManager(app)

    # to make current_user from jwt-extended work
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        # identity = jwt_data.get("sub") # returns the userId
        identity = jwt_data # dict contains user id, sub, etc
        return identity
```

- the error is gone
  - but the above initialization of jwt and the decorator should be outside of current app
    - initialize jwt in another file say extensions.py
	  - jwt = JWT_Manager()
  - and then in current app do: jwt.init_app(app)
  - this way jwt object can be referenced later in the code
  
  - see also: 
    - https://stackoverflow.com/questions/57335868/how-to-use-flask-jwt-extended-with-blueprints
    - app factories: https://flask.palletsprojects.com/en/2.3.x/patterns/appfactories/


