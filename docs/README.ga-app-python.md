# Notes on Graph Academy neo4j python course

## Important

- my app version:
  - github: https://github.com/pknag/ga-app-python
  - local: cloned in /home/DEV/Neo4j-Proj/ga-app-python
  - symlinked in ~/Projects/Neo4j-Proj/work
  
- working branch for code changes: academy

- copy of original app for inspection and copying code
  - ~/Store/Neo4j/GraphAcademy/app-python/
  - switch to branch to see code

- use auradb instance of the db
  - https://console.neo4j.io/?product=aura-db&tenant=aa1d098a-badb-48b7-9dcd-30bcad63f91f#databases/29cb2dee/detail
  
  - creds:
    - use port 7687
    - creds in original doc

## Investigate

- UI login creds do not last long
  - login through UI
  - propagates info to flask app
  - although token expiration is 360 days
    - JWT_EXPIRATION_DELTA is set in current_app = 360 days
  - reloading a page removes the login creds and have login again

## Routes

- register user: http://localhost:3000/register
- user login: http://localhost:3000/login

- list latest: http://localhost:3000/latest
- list popular: http://localhost:3000/popular

- to rate a movie: http://localhost:3000//ratings/<movie_id

- to set/unset favorite: http://localhost:3000/favorites/<movie_id>
- to list favorites list: http://localhost:3000/favorites

- to list genres: http://localhost:3000/genres
- to get genre details:   http://localhost:3000/genres/<genre_name>

- to get movies in a genre:  http://localhost:3000/genres/<name>/movies

- get movies by id: http://localhost:3000/movies/<movie_id>
- get similar movies:  http://localhost:3000/movies/{id}/similar

- get ratings for a movie: http://localhost:3000/<movie_id>/ratings

- get list of people: http://localhost:3000/people

## Notes start here

## Persistent user in UI
Mon Mar 11 2024

- notes in README.flask-problems.md



## challenge #15 - People profile
Mon Mar 11 2024

- https://graphacademy.neo4j.com/courses/app-python/3-backlog/7-person-view/

- switch locally to: git checkout 15-person-profile
  - for inspecting code
  
- routes:
  -  get people by the tmdbId: http://localhost:3000/people/<id>
    - route defined in: routes/people.py in meth: get_person(id)
	- code defined in: dao/people.py in meth: find_by_id(self, id)
  -  get all people similar to the person of tmdbId: http://localhost:3000/people/<id>/similar
    - route defined in: routes/people.py in meth: get_similar_people(id)
	- code defined in: dao/people.py in meth: get_similar_people(self, id, limit = 6, skip = 0)
  
- code:
  - find_by_id(self, id)
    - match a person by tmdbId (only actors and directors will have tmdbId)
	- returns person details plus: acted count and directed count
  - get_similar_people(id)
    - get people who acted AND/OR directed in the same movie
	- returns person details plus: acted count and directed count of the person
	- there is a difference in code between git and tutorial version in cypher code
	- think they do the same
	- git version
	
``` text
   def get_similar_people(self, id, limit = 6, skip = 0):
        # Get a list of similar people to the person by their id
        def get_similar_people(tx, id, skip, limit):
            result = tx.run("""
                MATCH (:Person {tmdbId: $id})-[:ACTED_IN|DIRECTED]->(m)<-[r:ACTED_IN|DIRECTED]-(p)
                RETURN p {
                    .*,
                    actedCount: count { (p)-[:ACTED_IN]->() },
                    directedCount: count { (p)-[:DIRECTED]->() }
                    inCommon: collect(m {.tmdbId, .title, type: type(r)})
                } AS person
                ORDER BY size(person.inCommon) DESC
                SKIP $skip
                LIMIT $limit
            """, id=id, skip=skip, limit=limit)

            return [ row.get("person") for row in result ]
```
	- tutorial version

``` text
   def get_similar_people(self, id, limit = 6, skip = 0):
        # Get a list of similar people to the person by their id
        def get_similar_people(tx, id, skip, limit):
            result = tx.run("""
                MATCH (:Person {tmdbId: $id})-[:ACTED_IN|DIRECTED]->(m)<-[r:ACTED_IN|DIRECTED]-(p)
                RETURN p {
                    .*,
                    actedCount: count { (p)-[:ACTED_IN]->() },
                    directedCount: count { (p)-[:DIRECTED]->() }
                    inCommon: collect(m {.tmdbId, .title, type: type(r)})
                } AS person
                ORDER BY size(person.inCommon) DESC
                SKIP $skip
                LIMIT $limit
            """, id=id, skip=skip, limit=limit)

            return [ row.get("person") for row in result ]
```

- db notes
  - you can set a param for a query in the browser
  - eg: :param id: "4724" to setup a query with a particular id
  

- pytest
  - fails on the git version
  - looks like it wants WITH statement

``` text
E       neo4j.exceptions.CypherSyntaxError: {code: Neo.ClientError.Statement.SyntaxError} {message: Aggregation column contains implicit grouping expressions. For example, in 'RETURN n.a, n.a + n.b + count(*)' the aggregation expression 'n.a + n.b + count(*)' includes the implicit grouping key 'n.b'. It may be possible to rewrite the query by extracting these grouping/aggregation expressions into a preceding WITH clause. Illegal expression(s): p (line 3, column 40 (offset: 123))
E       "                RETURN p {"
E                               }
}
```
  - use the tutorial version
    - passes the tests
	
``` text
(ga-app-python) pkn@ilish:/home/DEV/Neo4j-Proj/ga-app-python$ pytest -s tests/15_person_profile__test.py
========================================================= test session starts =========================================================
platform linux -- Python 3.11.8, pytest-7.1.3, pluggy-1.0.0
rootdir: /home/DEV/Neo4j-Proj/ga-app-python
collected 2 items                                                                                                                     

tests/15_person_profile__test.py .


Here is the answer to the quiz question on the lesson:
According to our algorithm, who is the most similar person to Francis Ford Coppola?
Copy and paste the following answer into the text box: 


Frederic Forrest
.

========================================================== warnings summary ===========================================================
tests/15_person_profile__test.py::test_should_return_paginated_list_of_similar_people
  /home/pkn/Store/Python/Anaconda/linux-conda-ilish/envs/ga-app-python/lib/python3.11/site-packages/neo4j/_sync/driver.py:493: DeprecationWarning: Relying on Driver's destructor to close the session is deprecated. Please make sure to close the session. Use it as a context (`with` statement) or make sure to call `.close()` explicitly. Future versions of the driver will not close drivers automatically.
    deprecation_warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
==================================================== 2 passed, 1 warning in 1.60s =====================================================
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
)
```

- UI tests
  - in peoples link click on a person
  - shows details and similar movies.
  - can change the sort order with choices: name, age, movie counts
  - urls
  
``` text
127.0.0.1 - - [11/Mar/2024 19:47:00] "GET /api/people/?sort=name&limit=4 HTTP/1.1" 200 -
127.0.0.1 - - [11/Mar/2024 19:47:04] "GET /api/people?sort=born&limit=4 HTTP/1.1" 308 -
127.0.0.1 - - [11/Mar/2024 19:47:08] "GET /api/people?sort=movieCount&limit=4 HTTP/1.1" 308 -
```
  
- commit

## challenge #14 - Listing people
Mon Mar 11 2024

- https://graphacademy.neo4j.com/courses/app-python/3-backlog/6-person-list/

- switch locally to: git checkout 14-person-list
  - for inspecting code
  
- routes:
  - get list of people: http://localhost:3000/people
    - route defined in: routes/people.py in meth: get_index()
	- code defined in: dao/people.py in meth: all(self, q, sort = 'name', order = 'ASC', limit = 6, skip = 0)
	
- code: all(self, q, sort = 'name', order = 'ASC', limit = 6, skip = 0)
  - find all people
  - if q is set then find the person with that name
  - return person name(s)
  - code in git is different from the tutorial
  - code in git is:
  
``` text
    def all(self, q, sort = 'name', order = 'ASC', limit = 6, skip = 0):
        # Get a list of people from the database
        def get_all_people(tx, q, sort, order, limit, skip):
            cypher = "MATCH (p:Person) "

            # If q is set, use it to filter on the name property
            if q is not None:
                cypher += "WHERE p.name CONTAINS $q"

            cypher += """
            RETURN p {{ .* }} AS person
            ORDER BY p.`{0}` {1}
            SKIP $skip
            LIMIT $limit
            """.format(sort, order)

            result = tx.run(cypher, q=q, sort=sort, order=order, limit=limit, skip=skip)

            return [ row.get("person") for row in result ]

        with self.driver.session() as session:
            return session.execute_read(get_all_people, q, sort, order, limit, skip)
```
  - code in tutorial is:
  
``` text
MATCH (p:Person)
WHERE $q IS NULL OR p.name CONTAINS $q
RETURN p { .* } AS person
ORDER BY p.name ASC
SKIP $skip
LIMIT $limit
```
  - then later the tutorial also has the same code as git
  
  - implemented the one in git
  
- pytest

``` text
(ga-app-python) pkn@ilish:/home/DEV/Neo4j-Proj/ga-app-python$ git commit -a
[academy 7c2d896] ch#13: Get ratings for a movie
 1 file changed, 22 insertions(+), 3 deletions(-)
(ga-app-python) pkn@ilish:/home/DEV/Neo4j-Proj/ga-app-python$ pytest -s tests/14_person_list__test.py
========================================================= test session starts =========================================================
platform linux -- Python 3.11.8, pytest-7.1.3, pluggy-1.0.0
rootdir: /home/DEV/Neo4j-Proj/ga-app-python
collected 3 items                                                                                                                     

tests/14_person_list__test.py ..Here is the answer to the quiz question on the lesson:
What is the name of the first person in the database in alphabetical order?
Copy and paste the following answer into the text box: 


 Aaron Woodley
.

========================================================== 3 passed in 2.38s ==========================================================
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
```

- challenge test
  - answer is: Aaron Woodley
  - but will not accept as correct
  - asks to run cypher in db to get answer

``` text
MATCH (p:Person)
RETURN p.name
ORDER BY p.name ASC LIMIT 1
```
  - answer is the same but the tutorial will not accept as correct
  - skip
  
- UI tests
  - seems to work
  
- commit

## challenge #13 - Listing Ratings
Mon Mar 11 2024

- https://graphacademy.neo4j.com/courses/app-python/3-backlog/5-listing-ratings/

- switch locally to: git checkout 13-listing-ratings
  - for inspecting code
  
- routes:
  - get ratings for a movie: http://localhost:3000/<movie_id>/ratings
    - route defined in routes/movies.py in meth: get_movie_ratings(movie_id)
	- code defined in dao/ratings.py in meth: for_movie(self, id, sort = 'timestamp', order = 'ASC', limit = 6, skip = 0)

- code: for_movie(self, id, sort = 'timestamp', order = 'ASC', limit = 6, skip = 0)
  - find all users who rated the movie given by its tmdbId
  - return rating, timestamp, and the users (userId and name)
  
- pytest

``` text
Author: Pranab Nag <pkn@pknandita.net>
(ga-app-python) pkn@ilish:/home/DEV/Neo4j-Proj/ga-app-python$ pytest -s tests/13_listing_ratings__test.py
========================================================= test session starts =========================================================
platform linux -- Python 3.11.8, pytest-7.1.3, pluggy-1.0.0
rootdir: /home/DEV/Neo4j-Proj/ga-app-python
collected 1 item                                                                                                                      

tests/13_listing_ratings__test.py 


Here is the answer to the quiz question on the lesson:
What is the name of the first person to rate the movie Pulp Fiction?
Copy and paste the following answer into the text box: 


Keith Howell
.

========================================================== 1 passed in 0.91s ==========================================================
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
```

- UI tests
  - list some movies (eg popular)
  - select a movie
  - can see a list of users with their ratings, user id, name
  
- commit


## challenge #12 - Getting movie details
Sun Mar 10 2024

- https://graphacademy.neo4j.com/courses/app-python/3-backlog/4-movie-view/

- switch locally to: git checkout 12-movie-details
  - for inspecting code

- routes:
  - get movies by id: http://localhost:3000/movies/<movie_id>
    - route in routes/movies.py: get_movie_details(movie_id)
	- code in dao/movies.py: find_by_id(self, id, user_id=None)
  - get similar movies:  http://localhost:3000/movies/{id}/similar
    - route in routes/movies.py: get_similar_movies(movie_id)
	- code in dao/movies.py: get_similar_movies(self, id, limit=6, skip=0, user_id=None)

- code: find_by_id
  - matches movie by tmdbId
  - returns the movie with additinal data: list of actors, list of directors, list of genres
    - and favorite flag set true for current user if any
- code: get_similar_movie
  - matches movie by tmdbId
  - finds other movies with common genre, or actor, or director
  - score = rating x number of movies in common
  - returns movies with additional data: score
    - and favorite flag set true for current user if any

- pytest

``` text
(ga-app-python) pkn@ilish:/home/DEV/Neo4j-Proj/ga-app-python$ pytest -s tests/12_movie_details__test.py
========================================================= test session starts =========================================================
platform linux -- Python 3.11.8, pytest-7.1.3, pluggy-1.0.0
rootdir: /home/DEV/Neo4j-Proj/ga-app-python
collected 2 items                                                                                                                     

tests/12_movie_details__test.py .Here is the answer to the quiz question on the lesson:
What is the title of the most similar movie to Lock, Stock & Two Smoking Barrels?
Copy and paste the following answer into the text box: 


Pulp Fiction
.

========================================================== 2 passed in 2.60s ==========================================================
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
(ga-app-python) pkn@ilish:/home/DEV/Neo4j-Proj/ga-app-python$ 

```

- UI Tests
  - no movie details shown
  - similar movies are displayed
  - error
  
``` text
  File "/home/DEV/Neo4j-Proj/ga-app-python/api/routes/movies.py", line 58, in get_movie_details
    return jsonify(movie)
           ^^^^^^^^^^^^^^
TypeError: Object of type Date is not JSON serializable
```

- debug:
  - added in get_movie_details(movie_id) in routes/movies.py
  - current_app.logger.debug(movie)
  - there are data in datetime format:
  - eg: 'born': neo4j.time.Date(1937, 6, 1)
  - jsonify cannot deal with this object type
  
- a solution
  - use json.dumps and json.loads to first convert the output in get_movie_details

``` text
import json
# convert neo4j.time.Date to string, so it can be serialized
result = first.get("movie")
result = json.dumps(result, indent=2, sort_keys=True, default = str) # convert all values to string, make it readable
result = json.loads(result)
return result
```

- the above solution works
  - UI shows the movie details and other stuff
  
- another solution:
  - https://github.com/neo4j-graphacademy/app-python/issues/10

``` text
Part of the Cypher query was rewritten, like this:
actors: [ (a)-[r:ACTED_IN]->(m) | a { .*, born: toString(a.born), died: toString(a.died), role: r.role } ],
As well as for directors.
```

- more notes in: README.flask-problems.md 
  - section: TypeError: Object of type Date is not JSON serializable

- final fix
- api/utils/json.py contains two methods
  - stringify_json
    - uses dumps and loads to create a str version of json
	- call it before running jsonify
	- eg in routes/movies.py in get_movie_details(movie_id)
	  - movie = stringify_json(movie)
	- works
  - NeoJsonProvider class
    - checks for neo4j.time.Date and converts to isoformat
    - in app set: app.json = NeoJsonProvider(app)
	- works
	
- cleanup and commit 


## challenge #11 - getting movie lists for genre, actor, director
Sun Mar 10 2024

- https://graphacademy.neo4j.com/courses/app-python/3-backlog/3-movie-lists/

- switch locally to: git checkout 11-movie-lists
  - for inspecting code

- routes:
  - to get movies in a genre:  http://localhost:3000/genres/<name>/movies
    - defined in api/routes/genres.py
	- uses api/dao/movies.py: get_by_genre()
	
  - list of movies by actor: no endpoint defined
    - api/dao/movies.py: get_for_actor()
  - list of movies by director: no endpoint defined
    - api/dao/movies.py: get_for_director()
	
- code: The code for three methods are similar

``` text
        def get_movies_in_genre(tx, sort, order, limit, skip, user_id):
            favorites = self.get_user_favorites(tx, user_id)

            cypher = """
                MATCH (m:Movie)-[:IN_GENRE]->(:Genre {{name: $name}})
                WHERE m.`{0}` IS NOT NULL
                RETURN m {{
                    .*,
                    favorite: m.tmdbId in $favorites
                }} AS movie
                ORDER BY m.`{0}` {1}
                SKIP $skip
                LIMIT $limit
            """.format(sort, order)

            result = tx.run(cypher, name=name, limit=limit, skip=skip, user_id=user_id, favorites=favorites)

            return [ row.get("movie") for row in result ]
```

- purpose

``` text
In this challenge, you will implement the remaining methods in the MovieDAO for retrieving a list of movies:
get_by_genre() - should return a paginated list of movies that are listed in a particular Genre
get_for_actor() - should return a paginated list of movies that a particular Person has acted in
get_for_director() - should return a paginated list of movies that a particular Person has directed
```

- pytest

``` text
(ga-app-python) pkn@ilish:/home/DEV/Neo4j-Proj/ga-app-python$ git commit -a
[academy 348a885] removed debug statements
 1 file changed, 3 deletions(-)
(ga-app-python) pkn@ilish:/home/DEV/Neo4j-Proj/ga-app-python$ pytest -s tests/11_movie_lists__test.py
========================================================= test session starts =========================================================
platform linux -- Python 3.11.8, pytest-7.1.3, pluggy-1.0.0
rootdir: /home/DEV/Neo4j-Proj/ga-app-python
collected 4 items                                                                                                                     

tests/11_movie_lists__test.py ...Here is the answer to the quiz question on the lesson:
How many films has Francis Ford Coppola directed?
Copy and paste the following answer into the text box: 


16
.

========================================================== 4 passed in 3.58s ==========================================================
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
```

- UI tests
  - list of movies for a genre works
  - can be sorted by title, release date, rating
  - endpoints are as follows
  
``` text
127.0.0.1 - - [10/Mar/2024 12:53:56] "GET /api/genres/Adventure/ HTTP/1.1" 200 -
127.0.0.1 - - [10/Mar/2024 12:53:56] "GET /api/genres/Adventure/movies?sort=title&limit=6 HTTP/1.1" 200 -
127.0.0.1 - - [10/Mar/2024 12:54:02] "GET /api/genres/Adventure/movies?sort=title&limit=6&skip=6 HTTP/1.1" 200 -
127.0.0.1 - - [10/Mar/2024 12:54:21] "GET /api/genres/Adventure/movies?sort=imdbRating&limit=6 HTTP/1.1" 200 -
127.0.0.1 - - [10/Mar/2024 12:54:34] "GET /api/genres/Adventure/movies?sort=title&limit=6 HTTP/1.1" 200 -
127.0.0.1 - - [10/Mar/2024 12:54:49] "GET /api/genres/Adventure/movies?sort=imdbRating&limit=6 HTTP/1.1" 200 -
127.0.0.1 - - [10/Mar/2024 12:54:52] "GET /api/genres/Adventure/movies?sort=title&limit=6 HTTP/1.1" 200 -

```
  - other endpoints cannot be tested
  
- commit

## challenge #10 - Finding genre details
Sun Mar 10 2024

- https://graphacademy.neo4j.com/courses/app-python/3-backlog/2-find-genre-details/

- switch locally to: git checkout 10-genre-details
  - for inspecting code

- route:
  - When the user clicks a genre in the list, they are taken to a list of movies for that genre. 
  - This list is populated by an API request to /api/genres/[name], for example http://localhost:3000/api/genres/Comedy.
  - actually:  http://localhost:3000/genres/Comedy
  - right now UI shows the same list of wrong movies and genre when a genre is clicked
  
- code: api/dao/genres.py
  - method: find(genre-name)
  
- purpose
  - given a genre by name

``` text
What does this query do?

This query uses the MATCH clause for a Genre node with the name passed through with the function call as a parameter. The query then finds the highest rated movie with a poster property and uses that image as the background to the card in the UI.

The size() function uses a precalculated value stored against the Genre node to return the number of incoming IN_GENRE relationships the Genre node.
```

- cypher error
  - had the same problem as before: use count instead of size for finding number of movies
  
- pytest

``` text
(ga-app-python) pkn@ilish:/home/DEV/Neo4j-Proj/ga-app-python$ pytest -s tests/10_genre_details__test.py
========================================================= test session starts =========================================================
platform linux -- Python 3.11.8, pytest-7.1.3, pluggy-1.0.0
rootdir: /home/DEV/Neo4j-Proj/ga-app-python
collected 1 item                                                                                                                      

tests/10_genre_details__test.py Here is the answer to the quiz question on the lesson:
How many movies are in the Action genre?
Copy and paste the following answer into the text box: 


1545
.

========================================================== 1 passed in 0.73s ==========================================================
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
```

- UI test
  - the info returned is not shown on screen
  - a list of movies (wrong) is still returned
  - the UI calls: GET /api/genres/Comedy/movies?sort=title&limit=6 for populating movies
    - this route is not implemented yet
	
- commit
  
## challenge #9 - Browsing genres
Sun Mar 10 2024

- https://graphacademy.neo4j.com/courses/app-python/3-backlog/1-browse-genres/

- switch locally to: git checkout 09-genre-list
  - for inspecting code

- route:
  - This list is populated by the API route at http://localhost:3000/api/genres, 
  - with the list being produced by the all() method within the GenreDAO.
  - actually: http://localhost:3000/genres
  
- code: api/dao/genres.py
  - method: all()
  
- purpose: return a list of genres witj
  - genre name
  - number of movies in the genre
  - poster: image of most popular movie in the genre
  
- cypher error (tested on db)
  - movies: size((g)<-[:IN_GENRE]-(:Movie)) cannot be used
  - use: movies: count { (g)<-[:IN_GENRE]-(:Movie) }
  - correct cypher
  - The inner CALL block finds the highest rated movie with a poster for each genre

``` text
            result = tx.run("""
                MATCH (g:Genre)
                WHERE g.name <> '(no genres listed)'
                CALL {
                    WITH g
                    MATCH (g)<-[:IN_GENRE]-(m:Movie)
                    WHERE m.imdbRating IS NOT NULL AND m.poster IS NOT NULL
                    RETURN m.poster AS poster
                    ORDER BY m.imdbRating DESC LIMIT 1
                }
                RETURN g {
                    .*,
                    movies: count { (g)<-[:IN_GENRE]-(:Movie) },
                    poster: poster
                } AS genre
                ORDER BY g.name ASC
            """)
```
  
- pytest

``` text
(ga-app-python) pkn@ilish:/home/DEV/Neo4j-Proj/ga-app-python$ pytest -s tests/09_genre_list__test.py
========================================================= test session starts =========================================================
platform linux -- Python 3.11.8, pytest-7.1.3, pluggy-1.0.0
rootdir: /home/DEV/Neo4j-Proj/ga-app-python
collected 1 item                                                                                                                      

tests/09_genre_list__test.py Here is the answer to the quiz question on the lesson:
Which genre has the highest movie count?
Copy and paste the following answer into the text box: 


Drama
.

========================================================== 1 passed in 0.75s ==========================================================
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
```

- UI Test
  - list genres
  - shows genres with a movie image in alphabetical order

- commit

## challenge #8 - Adding the favorite flag
Sat Mar 09 2024

- https://graphacademy.neo4j.com/courses/app-python/2-interacting/11-favorite-flag/

- switch locally to: git checkout 08-favorite-flag
  - for inspecting code

- purpose: When listing movies highlight/show which are the favorites of current user
  - return movies data with favorite flag set for the current user if any

- route: nothing special

- reason: 
  - the previous method populates my favorites list using the user id
    - collects all the favorite movies
  - whereas latest movies, popular movies uses a different method to collect movies
    - need to set the favorite flag for this list of movies
  
- the tutorial asks to modify api/dao/auth.py 
  - but it is wrong
  - should be api/dao/movies.py, 
  - method: get_user_favorites(self, tx, user_id)
    - returns a list of tmdbId of favorite movies of the user or empty list if there is no user logged in
  - method: get_movies
    - run the above unit of work first and then return a list of movies with favorite flag set

- pytest

``` text
(ga-app-python) pkn@ilish:/home/DEV/Neo4j-Proj/ga-app-python$ pytest tests/08_favorite_flag__test.py
========================================================= test session starts =========================================================
platform linux -- Python 3.11.8, pytest-7.1.3, pluggy-1.0.0
rootdir: /home/DEV/Neo4j-Proj/ga-app-python
collected 1 item                                                                                                                      

tests/08_favorite_flag__test.py .                                                                                               [100%]

========================================================== 1 passed in 1.50s ==========================================================
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
```

- UI test
  - works for signed in user
  - works for signed out user
  
- commit

## challenge #7 - My favorites list
Sat Mar 09 2024

- https://graphacademy.neo4j.com/courses/app-python/2-interacting/10-user-favorites/

- switch locally to: git checkout 07-favorites-list 
  - for inspecting code

- code: 
  - api/routes/account.py: def add_favorite(movie_id)
  - endpoint is: /api/favorites/{id}
  - supports POST and DELETE
  - instantiates FavoriteDAO
  
- purpose: user toggles favorite bookmark
  - and favorites link shows all the favorites of a user
  
- route: 
  - to set/unset favorite: http://localhost:3000/favorites/<movie_id>
  - to list favorites list: http://localhost:3000/favorites
  - in account.py
  
- the tutorial asks to modify api/dao/auth.py 
  - but it is wrong

- modify api/dao/favorites.py
  - add() method to add a favorite movie
  - all() to list all favorite movies
  - remove() to remove a favorite movie

- copy code
  - it seems all method has syntax error in cypher statement
  - uses double parenthesis {{}} 
  - should be single {}
  - tutorial says that double parenthesis needed by python to escape it
  - but the other two methods (add, remove) do not have double parenthesis
  
``` text
MATCH (u:User {{userId: $userId}})-[r:HAS_FAVORITE]->(m:Movie)
RETURN m {{
         .*,
         favorite: true
         }} AS movie
ORDER BY m.`{0}` {1}
SKIP $skip
LIMIT $limit
```
 
- pytest

``` text
(ga-app-python) pkn@ilish:/home/DEV/Neo4j-Proj/ga-app-python$ pytest tests/07_favorites_list__test.py
========================================================= test session starts =========================================================
platform linux -- Python 3.11.8, pytest-7.1.3, pluggy-1.0.0
rootdir: /home/DEV/Neo4j-Proj/ga-app-python
collected 4 items                                                                                                                     

tests/07_favorites_list__test.py ....                                                                                           [100%]

========================================================== 4 passed in 4.15s ==========================================================
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
```

- UI tests
  - login as auth if needed
  - pick some movie and select bookmark in top left corner
  - ui shows success
  - endpoints: 
    - "POST /api/account/favorites/278 HTTP/1.1" 200
	- "POST /api/account/favorites/238 HTTP/1.1" 200 -
  - select favorites
    - shows the two movie selected as favorites.
	- seems like all() method works

- check db
  - looks good

``` text
MATCH (n:User)-[r:HAS_FAVORITE]->(m:Movie)
RETURN n LIMIT 25;
```

- UI test to remove favorite
  - click the bookmark again
  - works
  - db query shows it worked
  
- commit

## challenge #6 - Movie Ratings
Sat Mar 09 2024

- https://graphacademy.neo4j.com/courses/app-python/2-interacting/9-ratings/

- switch locally to: git checkout 06-rating-movies
  - for inspecting code

- edited api/dao/ratings.py class RatingsDAO
  - method add() was modified
  - endpoint: "POST /api/account/ratings/769"
  - invokes save_rating(movie_id) in api/routes/account.py

- routes:
  - http://localhost:3000//ratings/<movie_id
  - in account.py
  
- process

``` text
When the form is submitted, the website sends a request to /api/account/ratings/{movieId} and the following will happen:
The server directs the request to the route handler in api/routes/account.py, which verifies the user’s JWT token before handling the request.
The route handler creates an instance of the RatingDAO.
The add() method is called on the RatingDAO, and is passed the ID of the current user, the ID of the movie and a rating from the request body.
It is then the responsibility of the add() method to save this information to the database and return an appropriate response.
```

- pytest

``` text
(ga-app-python) pkn@ilish:/home/DEV/Neo4j-Proj/ga-app-python$ pytest tests/06_rating_movies__test.py
========================================================= test session starts =========================================================
platform linux -- Python 3.11.8, pytest-7.1.3, pluggy-1.0.0
rootdir: /home/DEV/Neo4j-Proj/ga-app-python
collected 1 item                                                                                                                      

tests/06_rating_movies__test.py .                                                                                               [100%]

========================================================== 1 passed in 1.11s ==========================================================
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
```

- UI test
  - login as mmm
  - pick a movie and rate
  - works but it is always the same movie that is picked
  - because find_by_id method in da0/movies.py always returns Goodfellas

- check 
  - looks good. MMM rated Goodfellas 3
  
- commit
  
## UI quirks
Sat Mar 09 2024

- after logging in as mmm@mmm.com
  - reloading web page clears the login
- but clicking on other links/features on the web page keeps the user logged in
- reloading causes auth failure
  - no other clue yet

## Solving Flask JWT error
Sat Mar 09 2024

- see: README.flask-problems.md

- current_user from flask-jwt-extended returns errors when used in methods such as in
  - routes/movies.py

## challenge #5 - Authenticating a User
Fri Mar 08 2024

- https://graphacademy.neo4j.com/courses/app-python/2-interacting/8-authenticating/

- switch locally to: git checkout 05-authentication 
  - for inspecting code

- route: http://localhost:3000/api/login

- When a user attempts to access an API endpoint that requires authentication, the server checks for a JWT token.
  - When a user registers or signs in, a JWT token is generated and appended to the User record. 
  - This token is then stored by the UI and appended to Bearer to create an authorization header.
  - The token generation happens in the AuthDAO using the _generate_token() method.
  - When The API receives a request which includes the authorization header, the Flask-JWT library attempts to decode the value and makes the payload available by importing current_user from flask_jwt.
  
- code: api/dao/auth.py: AuthDAO
  - method: authenticate()
  - add code
  
- pytest

``` text
(ga-app-python) pkn@ilish:/home/DEV/Neo4j-Proj/ga-app-python$ pytest tests/05_authentication__test.py
========================================================= test session starts =========================================================
platform linux -- Python 3.11.8, pytest-7.1.3, pluggy-1.0.0
rootdir: /home/DEV/Neo4j-Proj/ga-app-python
collected 4 items                                                                                                                     

tests/05_authentication__test.py ....                                                                                           [100%]

========================================================== 4 passed in 3.50s ==========================================================
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
```

- create user in UI
  - MMM com, mmm@mmm@gmail.com, abcdef
  - flask still throws an error
  
``` text
 line 96, in get_current_user
    raise RuntimeError(
RuntimeError: You must provide a `@jwt.user_lookup_loader` callback to use this method)
```

- login
  - logout first
  - then login ass mmm@mmm.com
  - works
  - flask still throws the same error
    - cannot get the current used
  - no movies are shown on the first page though


## challenge #4 - Unique email addresses
Fri Mar 08 2024

- https://graphacademy.neo4j.com/courses/app-python/2-interacting/7-unique-emails/

- switch locally to: 04-handle-constraint-errors
  - for inspecting code

- current implementation does not check whether email address is unique
  - fix it by adding an unique constraint to the db
  - and then check for exeception in code
  
- code: api/dao/auth.py: AuthDAO
  - the validation code was already added earlier
  
- add constraint in aura db browser

``` text
CREATE CONSTRAINT UserEmailUnique
IF NOT EXISTS
FOR (user:User)
REQUIRE user.email IS UNIQUE;
```

- run pytest
  - pytest code does not close the session
  - not my problem

``` text
(ga-app-python) pkn@ilish:/home/DEV/Neo4j-Proj/ga-app-python$ pytest tests/04_handle_constraint_errors__test.py
========================================================= test session starts =========================================================
platform linux -- Python 3.11.8, pytest-7.1.3, pluggy-1.0.0
rootdir: /home/DEV/Neo4j-Proj/ga-app-python
collected 2 items                                                                                                                     

tests/04_handle_constraint_errors__test.py ..                                                                                   [100%]

========================================================== warnings summary ===========================================================
tests/04_handle_constraint_errors__test.py::test_validation_error
  /home/pkn/Store/Python/Anaconda/linux-conda-ilish/envs/ga-app-python/lib/python3.11/site-packages/neo4j/_sync/driver.py:493: DeprecationWarning: Relying on Driver's destructor to close the session is deprecated. Please make sure to close the session. Use it as a context (`with` statement) or make sure to call `.close()` explicitly. Future versions of the driver will not close drivers automatically.
    deprecation_warn()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
==================================================== 2 passed, 1 warning in 2.19s =====================================================
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
```

- commit code

- test user registration in UI
  - registered pkn.nag@gmail.com
  - pass: Chutia
  - throws error but user is registered
  
``` text
payload["token"] = self._generate_token(payload)
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
key = force_bytes(key)
          ^^^^^^^^^^^^^^^^
  File "/home/pkn/Store/Python/Anaconda/linux-conda-ilish/envs/ga-app-python/lib/python3.11/site-packages/jwt/utils.py", line 22, in force_bytes
    raise TypeError("Expected a string value")
```
- but the user is created - Hmm
  - should catch random errors in register function
  - trying to add another user with same email throws an error and is displayed in UI
  
- test with another user registeration in UI
  - for debugging
  - jwt_secret is None and causing problems
  - pytest does show this error since it uses its own secret key
  - error is in api/routes/auth.py
    - flask app sets JWT_SECRET_KEY but routes/auth.py uses SECRET_KEY
	- fixed it
	
- test again with a new user
  - the above error is gone
  - JWT secret is used correctly now
  - UI immediately logins as the new user: ABC Ltd
  - flask throws and error
  - probably because there is no useful login method - ignoring
  
- commit
	
## challenge #3 - User Registration
Fri Mar 08 2024

- https://graphacademy.neo4j.com/courses/app-python/2-interacting/5-registering/

- switch locally to: git checkout 03-registering-a-user
  - for inspecting code
  
- api/dao/auth.py: AuthDAO
  - add code

- route: http://localhost:3000/api/auth/register
  - actually: http://localhost:3000/register
  - because it is remapped in code
  - for login: http://localhost:3000/login
  
- takes as input: User Name, email, plain password
  - encrypts the password
  - creates a user with self generated user id
  - the return info/payload (userid, encrypted pass, email, etc) is used to generate a token using jwt
    - expects a secret key
  - the token is added to the payload and returned to the caller
  - the token is used for future requests
  
- pytest

``` text
(ga-app-python) pkn@ilish:/home/DEV/Neo4j-Proj/ga-app-python$ pytest tests/03_registering_a_user__test.py
========================================================= test session starts =========================================================
platform linux -- Python 3.11.8, pytest-7.1.3, pluggy-1.0.0
rootdir: /home/DEV/Neo4j-Proj/ga-app-python
collected 1 item                                                                                                                      

tests/03_registering_a_user__test.py .                                                                                          [100%]

========================================================== 1 passed in 1.30s ==========================================================
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
```

- test in neo browser
  - success
  
``` text
MATCH (n:User) 
WHERE n.password is not NULL
RETURN n LIMIT 25;
```
- git commit

## challenge #2 - Home page
Fri Mar 08 2024

- https://graphacademy.neo4j.com/courses/app-python/2-interacting/4-home-page/
- switch locally to: git checkout 02-movie-lists

- DAO: data access object pattern
  - eg: https://stackoverflow.com/questions/69677507/data-access-object-dao-in-python-flask-sqlalchemy
  - keep business logic separate from db
  
- api/dao/movies.py: MovieDAO
- define all() method
  - a function: def get_movies(tx, sort, order, limit, skip, user_id):
  - an run a read transaction on the above function

- routes:
  - http://localhost:3000/latest
  - http://localhost:3000/popular
  
- test with flask: reload the main page
  - the method gets called twice: Latest and Popular
  - (sort, order, limit, skip, user_id) = released desc 6 0 None
  - (sort, order, limit, skip, user_id) = imdbRating desc 6 0 None

- pytest: 

``` text
(ga-app-python) pkn@ilish:/home/DEV/Neo4j-Proj/ga-app-python$ pytest -s tests/02_movie_list__test.py
========================================================= test session starts =========================================================
platform linux -- Python 3.11.8, pytest-7.1.3, pluggy-1.0.0
rootdir: /home/DEV/Neo4j-Proj/ga-app-python
collected 2 items                                                                                                                     

tests/02_movie_list__test.py .Here is the answer to the quiz question on the lesson:
What is the title of the highest rated movie in the recommendations dataset?
Copy and paste the following answer into the text box:

Band of Brothers
.

========================================================== 2 passed in 1.85s ==========================================================
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
```
- commit

## challenge #1 neo4j driver
Fri Mar 08 2024

- https://graphacademy.neo4j.com/courses/app-python/1-driver/3-connecting/

- edited code: copied from 01-connect-to-neo4j
- run tests: pytest tests/01_connect_to_neo4j__test.py
  - passes 4 tests but there were some error messages at the end

``` text
(ga-app-python) pkn@ilish:/home/DEV/Neo4j-Proj/ga-app-python$ pytest tests/01_connect_to_neo4j__test.py
========================================================= test session starts =========================================================
platform linux -- Python 3.11.8, pytest-7.1.3, pluggy-1.0.0
rootdir: /home/DEV/Neo4j-Proj/ga-app-python
collected 4 items                                                                                                                     

tests/01_connect_to_neo4j__test.py ....                                                                                         [100%]

========================================================== 4 passed in 1.45s ==========================================================
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection ResolvedIPv4Address(('34.121.155.65', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
Failed to write data to connection IPv4Address(('29cb2dee.databases.neo4j.io', 7687)) (ResolvedIPv4Address(('34.121.155.65', 7687)))
```
- commit

## Create working branch
Fri Mar 08 2024

- switch to main
  - add .idea dir, commit and push
  
- new branch name: academy
  - git checkout -b academy 
    - creates a new branch based on academy and switches to it
  - setup remote
    - git push -u origin academy
	- this creates the remote tracking branch

- create .env from sample
  - .env is ignored by git
  - .env

``` text
FLASK_APP=api
FLASK_DEBUG=true
FLASK_RUN_PORT=3000

- neo4j password creds in original doc

JWT_SECRET=mysupersecret
SALT_ROUNDS=10
```

- test flask: 
  - activate env: conda activate ga-app-python
  - at root dir: flask run
  - app is on localhost:3000
  - works with some prepopulated data from api/data.py
  

## Fork app-python on github
Thu Mar 07 2024

- tried a plain fork on github
  - the repo tracks the original repo
  - want to have my own copy on github without tracking neo4j's repo

- Created a clone on github
  - https://github.com/pknag/ga-app-python
  - cloned in /home/DEV/Neo4j-Proj/ga-app-python
  - symlinked in ~/Projects/Neo4j-Proj/work
  - for details of doing this: Store/Git/cloning-moving-repository.md

- create conda env: ga-app-python
  - see README.ga-app-python.md in conda Environments
  - used conda to create env
  - used pip to install all other dependencies

- configure pycharm
  - add conda env

## Transfer data to AuraDB
Thu Feb 29 2024

- sandbox is valid for 3 days and can be extended for 7 days
  - auradb is free for one instance
  
- take backup from neo4j sandbox in python app course
  - creates a .dump file, rename to: reccomendation-db.dump
  - stored in academy-data dir

- Start a new auradb instance
  - Instance01: Renamed to Reccomendations
  - bolt url: neo4j+s://neo4j@29cb2dee.databases.neo4j.io:7687
  - pass: ZQucyl4wJKNt4TguqXFzJ5n5XyU80IozHviFS2TiiDY
  - Username: neo4j
  
- Import the dump file
  - go to: https://console.neo4j.io/
  - click the instance name: eg Instance01
    - do not select Open as it will open an interface to the DB only
  - three tabs will appear: Snapshots, Import Database, Logs
  - select 'Import Database'
  
## Neo4j python app - course summary
Thu Feb 29 2024

- sandbox used: https://sandbox.neo4j.com/?usecase=recommendations
  - terminated since course completed
  
- sandbox can be created again
  - instructions at: https://graphacademy.neo4j.com/courses/app-python/0-setup/1-setup/

## Neo4j python app - contd
Thu Feb 29 2024

- code challenge #2
  - https://graphacademy.neo4j.com/courses/app-python/2-interacting/4-home-page/

- open code from course
  - creates a new workspace: https://neo4jgraphaca-apppython-1nzu60pga8j.ws-us108.gitpod.io/
    - sandbox creds are the same
  - run pip install neo4j
  - delete the old workspace
  - just do not use the graph academy way of opening files
  
- switch branch to: 02-movie-lists
  
- run the app in terminal
  - at top level run in terminal

``` text
export FLASK_APP=api
export FLASK_ENV=development
flask run
```
  - terminal messages
  
``` text
gitpod /workspace/app-python (main) $ export FLASK_APP=api
gitpod /workspace/app-python (main) $ export FLASK_ENV=development
gitpod /workspace/app-python (main) $ flask run
'FLASK_ENV' is deprecated and will not be used in Flask 2.3. Use 'FLASK_DEBUG' instead.
'FLASK_ENV' is deprecated and will not be used in Flask 2.3. Use 'FLASK_DEBUG' instead.
'FLASK_ENV' is deprecated and will not be used in Flask 2.3. Use 'FLASK_DEBUG' instead.
 * Serving Flask app 'api'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
'FLASK_ENV' is deprecated and will not be used in Flask 2.3. Use 'FLASK_DEBUG' instead.
'FLASK_ENV' is deprecated and will not be used in Flask 2.3. Use 'FLASK_DEBUG' instead.
'FLASK_ENV' is deprecated and will not be used in Flask 2.3. Use 'FLASK_DEBUG' instead.
 * Debugger is active!
 * Debugger PIN: 144-850-973
```

  - open browser: gitpod detects port 5000 has a server
    - tutorial says port 3000 though
	- flask default port is 5000 looks like
    - gui browser opens
	
- add another bash terminal in gitpod to do other tasks

- api/dao/movies.py
  - code here changed

- running pytest results in error
  - pytest -s tests/02_movie_list__test.py
  - exists clause is invalid in this version
    - new: WHERE exists(m.`{0}`)
	- orig:  WHERE m.`{0}` IS NOT NULL
	

``` python
    """
     This method should return a paginated list of movies ordered by the `sort`
     parameter and limited to the number passed as `limit`.  The `skip` variable should be
     used to skip a certain number of rows.

     If a user_id value is suppled, a `favorite` boolean property should be returned to
     signify whether the user has added the movie to their "My Favorites" list.
    """
    # tag::all[]
    def all(self, sort, order, limit=6, skip=0, user_id=None):
        # tag::get_movies[]
        # Define the Unit of Work
        def get_movies(tx, sort, order, limit, skip, user_id):
        # tag::end_movies[]
            # tag::all_cypher[]
            # Define the cypher statement
            cypher = """
                MATCH (m:Movie)
                WHERE m.`{0}` IS NOT NULL
                RETURN m {{ .* }} AS movie
                ORDER BY m.`{0}` {1}
                SKIP $skip
                LIMIT $limit
            """.format(sort, order)

            # Run the statement within the transaction passed as the first argument
            result = tx.run(cypher, limit=limit, skip=skip, user_id=user_id)
            # end::all_cypher[]

            # tag::allmovies[]
            # Extract a list of Movies from the Result
            return [row.value("movie") for row in result]
            # end::allmovies[]
        
        # tag::return[]
        # tag::session[]
        with self.driver.session() as session:
        # end::session[]
            return session.execute_read(get_movies, sort, order, limit, skip, user_id)
            # end::return[]
    # end::all[]

```

## Neo4j python app - contd
Thu Feb 29 2024

- Handling Driver Errors
  - https://graphacademy.neo4j.com/courses/app-python/2-interacting/6-driver-errors/
  
  - In the Neo4j Python Driver, an error extending the neo4j.exceptions.Neo4jError class will be thrown.

- error codes: There are many listed 

- You can catch the specific exception above within a try/catch block, or catch all Neo4jErrors instances:

``` text
# Import the Exception classes from neo4j.exceptions
from neo4j.exceptions import Neo4jError, ConstraintError

# Attempt a query
try:
    tx.run(cypher, params)
except ConstraintError as err:
    print("Handle constaint violation")
    print(err.code) # (1)
    print(err.message) # (2)
except Neo4jError as err:
    print("Handle generic Neo4j Error")
    print(err.code) # (1)
    print(err.message) # (2)
```

- Error Codes
  - The Neo4jError includes a code property, which provides higher-level information about the query.
  - Each status code follows the same format, and includes four parts:

``` text
Neo.[Classification].[Category].[Title]
(1)        (2)          (3)       (4)
```

  1. Every Neo4j Error code is prefixed with Neo.
  2. The Classification provides a high-level classification of the error - for example, a client-side error or an error with the database.
  3. The Category provides a higher-level category for the error - for example, a problem with clustering, a procedure or the database schema.
  4. The Title provides specific information about the error that has occurred.

  - For a comprehensive list of status codes, see Status Codes in the Neo4j Documentation.
    - https://neo4j.com/docs/status-codes/current/

## Neo4j python app - contd
Thu Feb 29 2024

- Neo4j type system
  - https://graphacademy.neo4j.com/courses/app-python/2-interacting/3-type-system/
  
- python to neo4j
  - there are more like, datetime, spatial types that have python mapping
  - time: https://graphacademy.neo4j.com/courses/app-python/2-interacting/3-type-system/#_temporal_data_types
  - spatial: https://graphacademy.neo4j.com/courses/app-python/2-interacting/3-type-system/#_spatial_data_types
  - nodes and relationships: https://graphacademy.neo4j.com/courses/app-python/2-interacting/3-type-system/#_nodes_relationships
  
``` text
Python Type 	Neo4j Cypher Type 	Notes

None            null
bool            Boolean
int             Integer
float           Float
str             String
bytearray       Bytes [1]
list            List
dict            Map
```

- Nodes & Relationships
  - Nodes and Relationships are both returned as similar classes.
  - As an example, let’s take the following code snippet:
  - The query will return one record for each :Person and :Movie node with an :ACTED_IN relationship between them.
  
``` text
result = tx.run("""
MATCH path = (person:Person)-[actedIn:ACTED_IN]->(movie:Movie {title: $title})
RETURN path, person, actedIn, movie
""", title=movie)
```
- Nodes
  - We can retrieve the movie value from a record using the [] brackets method, providing a string that refers to the alias for the :Movie node in the Cypher statement.
  
``` text
for record in result:
    node = record["movie"]
```
  - The value assigned to the node variable will be the instance of a Node. 
  - Node is a type provided by the Neo4j Python Driver to hold the information held in Neo4j for the node.

``` text
print(node.id)              # (1)
print(node.labels)          # (2)
print(node.items())         # (3)

# (4)
print(node["name"])
print(node.get("name", "N/A"))
```

  - The id property provides access to the node’s Internal ID
    eg. 1234
  - The labels property is a frozenset containing an array of labels attributed to the Node
    eg. ['Person', 'Actor']
  - The items() method provides access to the node’s properties as an iterable of all name-value pairs.
    eg. {name: 'Tom Hanks', tmdbId: '31' }
  - A single property can be retrieved by either using [] brackets or using the get() method. The get() method also allows you to define a default property if none exists.

  - Internal IDs
    - Internal IDs refer to the position in the Neo4j store files where the record is held. 
	- These numbers can be re-used, 
	- a best practice is to always look up a node by an indexed property rather than relying on an internal ID.
	
- Relationships
  - Relationship objects are similar to a Node in that they provide the same method for accessing the internal ID and properties.
	
``` text
acted_in = record["actedIn"]

print(acted_in.id)         # (1)
print(acted_in.type)       # (2)
print(acted_in.items())    # (3)

# 4
print(acted_in["roles"])
print(acted_in.get("roles", "(Unknown)"))

print(acted_in.start_node) # (5)
print(acted_in.end_node)   # (6)
```
  - The id property holds the internal ID of the relationship.
    eg. 9876
  - The type property holds the relationship type
    eg. ACTED_IN
  - The items() method provides access to the relationships’s properties as an iterable of all name-value pairs.
    eg. {role: 'Woody'}
  - As with Nodes, you can access a single relationship property using brackets or the get() method.
  - start_node - an integer representing the internal ID for the node at the start of the relationship
  - end_node - an integer representing the internal ID for the node at the end of the relationship

- Paths
  - If you return a path of nodes and relationships, they will be returned as an instance of a Path.

``` text
path = record["path"]

print(path.start_node)  # (1)
print(path.end_node)    # (2)
print(len(path))  # (1)
print(path.relationships)  # (1)
```
  - start_node - a Neo4j Integer representing the internal ID for the node at the start of the path
  - end_node - a Neo4j Integer representing the internal ID for the node at the end of the path
  - len(path) - A count of the number of relationships within the path
  - relationships - An array of Relationship objects within the path.

- Path Segments
  - A path is split into segments representing each relationship in the path. For example, say we have a path of (p:Person)-[:ACTED_IN]→(m:Movie)-[:IN_GENRE]→(g:Genre), there would be two relationships.

    - (p:Person)-[:ACTED_IN]→(m:Movie)
    - (m:Movie)-[:IN_GENRE]→(g:Genre)
  
  - The relationships within a path can be iterated over using the iter() function.
  
``` text
for rel in iter(path):
    print(rel.type)
    print(rel.start_node)
    print(rel.end_node)
```

- Temporal Data types
  - Temporal data types are implemented by the neo4j.time module.
  - It provides a set of types compliant with ISO-8601 and Cypher, which are similar to those found in the built-in datetime module. Sub-second values are measured to nanosecond precision and the types are compatible with pytz.
  - The table below shows the general mappings between Cypher and the temporal types provided by the driver.
  - In addition, the built-in temporal types can be passed as parameters and will be mapped appropriately.
  
``` text
Neo4j Cypher Type 	Python driver type 	Python built-in type 	tzinfo

Date                neo4j.time.Date     datetime.date
Time                neo4j.time.Time     datetime.time           not None
LocalTime           neo4j.time.Time     datetime.time           None
DateTime            neo4j.time.DateTime datetime.datetime       not None
LocalDateTime       neo4j.time.DateTime datetime.datetime       None
Duration            neo4j.time.Duration datetime.timedelta
```
  - eg:
    
``` text
# Create a DateTime instance using individual values
datetime = neo4j.time.DateTime(year, month, day, hour, minute, second, nanosecond)

#  Create a DateTime  a time stamp (seconds since unix epoch).
from_timestamp = neo4j.time.DateTime(1609459200000) # 2021-01-01

# Get the current date and time.
now = neo4j.time.DateTime.now()

print(now.year) # 2022
```
  - Each of the above types has a number of attributes for accessing the different, for example year, month, day, and in the case of the types that include a time, hour, minute and second.
  - For more information, see Temporal Data Types: https://neo4j.com/docs/api/python-driver/4.4/temporal_types.html
  
- Spatial Data Types
  - Cypher has built-in support for handling spatial values (points), and the underlying database supports storing these point values as properties on nodes and relationships.

- Points

``` text
Cypher Type 	   Python Type

Point              neo4j.spatial.Point
Point (Cartesian)  neo4j.spatial.CartesianPoint
Point (WGS-84)     neo4j.spatial.WGS84Point
```

- CartesianPoint
  - A Cartesian Point can be created in Cypher by supplying x and y values to the point() function. The optional z value represents the height.
  - To create a Cartesian Point in Python, you can import the neo4j.spatial.CartesianPoint class.
  
``` text
# Using X and Y values
twoD=CartesianPoint((1.23, 4.56))
print(twoD.x, twoD.y)

# Using X, Y and Z
threeD=CartesianPoint((1.23, 4.56, 7.89))
print(threeD.x, threeD.y, threeD.z)
```
  - For more information, see the Python reference: https://neo4j.com/docs/api/python-driver/current/api.html#cartesianpoint

- WGS84Point
  - A WGS84 Point can be created in Cypher by supplying latitude and longitude values to the point() function. 
  - To create a Cartesian Point in Python, you can import the neo4j.spatial.WGS84Point class.
  
``` text
london=WGS84Point((-0.118092, 51.509865))
print(london.longitude, london.latitude)

the_shard=WGS84Point((-0.086500, 51.504501, 310))
print(the_shard.longitude, the_shard.latitude, the_shard.height)
```
  - For more see python reference: https://neo4j.com/docs/api/python-driver/current/api.html#wgs84point

- Distance
  - When using the point.distance function in Cypher, the distance calculated between two points is returned as a float.
  
``` text
WITH point({x: 1, y:1}) AS one,
     point({x: 10, y: 10}) AS two

RETURN point.distance(one, two) // 12.727922061357855
```
  - For more information on Spatial types, see the Cypher Manual: 
    - https://neo4j.com/docs/cypher-manual/current/values-and-types/spatial/
  
## Neo4j python app - contd
Thu Feb 29 2024

- Processing Results
  - https://graphacademy.neo4j.com/courses/app-python/2-interacting/2-results/
  
  - Query results are typically consumed as a stream of records. The drivers provide a way to iterate through that stream.
    - RETURN statement produces a record for each row of result
	- each record has keys from the return statment
	- eg in the following there will be one key 'p' for a record

``` python
# Unit of work
def get_actors(tx, movie): # (1)
    result = tx.run("""
        MATCH (p:Person)-[:ACTED_IN]->(:Movie {title: $title})
        RETURN p
    """, title=movie)

    # Access the `p` value from each record
    return [ record["p"] for record in result ]

# Open a Session
with driver.session() as session:
    # Run the unit of work within a Read Transaction
    actors = session.execute_read(get_actors, movie="The Green Mile") # (2)

    for record in actors:
        print(record["p"])

    session.close()
```

  - Peeking at results without consuming it

``` text
# Check the first record without consuming it
peek = result.peek()
print(peek)
```

  - Keys in records

``` text
# Get all keys available in the result
print(result.keys()) # eg. ["p", "roles"]
```

  - Single Result
    - If you only expect a single record, you can use the single() method on the result to return the first record.
	- If more than one record is available from the result then a warning will be generated, but the first result will still be returned. 
	- If no results are available, then the method call will return None.
	
``` text
def get_actors_single(tx, movie):
    result = tx.run("""
        MATCH (p:Person)-[:ACTED_IN]->(:Movie {title: $title})
        RETURN p
    """, title=movie)

    return result.single()
```
  - Value
    - If you wish to extract a single value from the remaining list of results, you can use the value() method.
	- The key or index of the field to return for each remaining record, and returns a list of single values.
    - Optionally, you can provide a default value to be used if the value is None or unavailable.
	
``` text
def get_actors_values(tx, movie):
    result = tx.run("""
        MATCH (p:Person)-[r:ACTED_IN]->(m:Movie {title: $title})
        RETURN p.name AS name, m.title AS title, r.roles AS roles
    """, title=movie)

    return result.value("name", False)
    # Returns the `name` value, or False if unavailable
```

  - Values
    - If you need to extract more than one item from each record, use the values() method. 
	- The method expects one parameter per item requested from the RETURN statement of the query.
	- In the above example, a list will be returned, with each entry containing values representing name, title, and roles.
	
``` text
def get_actors_values(tx, movie):
    result = tx.run("""
        MATCH (p:Person)-[r:ACTED_IN]->(m:Movie {title: $title})
        RETURN p.name AS name, m.title AS title, r.roles AS roles
    """, title=movie)

    return result.values("name", "title", "roles")
```
  
   - Consume
     - The consume() method will consume the remainder of the results and return a Result Summary.
	 
``` text
def get_actors_consume(tx, name):
    result = tx.run("""
        MERGE (p:Person {name: $name})
        RETURN p
    """, name=name)

    info = result.consume()
```
     - The Result Summary contains a information about the server, the query, execution times and a counters object which provide statistics about the query.
   
``` text
# The time it took for the server to have the result available. (milliseconds)
print(info.result_available_after)

# The time it took for the server to consume the result. (milliseconds)
print(info.result_consumed_after) 
```
     - The counters object can be used to retrieve the number of nodes, relationships, properties or labels that were affected during a write transaction.


``` text
print("{0} nodes created".format(info.counters.nodes_created))
print("{0} properties set".format(info.counters.properties_set))
```
     - more: https://neo4j.com/docs/api/python-driver/4.4/api.html#neo4j.ResultSummary
	 
  - Exploring Records
	- When accessing a record, either within a loop, list comprehension or within a single record, you can use the [] bracket syntax.
    - The following example extracts the p value from each record in the result buffer.
	
``` text
for record in result:
    print(record["p"]) # Person Node
```
   - You can also access a value using its index, as it relates to the value contained in the keys array:
     - eg: 0 for p, 1 for roles
	 
``` text
# Get all keys available in the result
print(result.keys()) # ["p", "roles"]
```
   
   
## Neo4j python app - contd
Wed Feb 28 2024

- Interacting with Neo4j
  - https://graphacademy.neo4j.com/courses/app-python/2-interacting/
  
- Sessions and transactions
  - https://graphacademy.neo4j.com/courses/app-python/2-interacting/1-transactions/
  - A session is a container for a sequence of transactions. 
  - Sessions borrow connections from a pool as required and are considered lightweight and disposable.
  - open a session
    - with driver.session(database="people") as session:
    - defaults to database=neo4j configured in neo4j.conf

  - The default access mode is set to write, but this can be overwritten by explicitly calling the execute_read() or execute_write() functions.
  
- Transactions
  
  - a transaction processes a "Unit of work"
  
  - autocommit transactions
    - uses sesssion.run method
	- can pass a cypher statement
	- should not be used in production, only for testing

  - read transactions
  
``` python
# Define a Unit of work to run within a Transaction (`tx`)
def get_movies(tx, title):
    return tx.run("""
        MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
        WHERE m.title = $title // (1)
        RETURN p.name AS name
        LIMIT 10
    """, title=title)

# Execute get_movies within a Read Transaction
session.execute_read(get_movies,
    title="Arthur" # (2)
)
```

  - write transactions
  
``` python
# Call tx.run() to execute the query to create a Person node
def create_person(tx, name):
    return tx.run(
        "CREATE (p:Person {name: $name})",
        name=name
    )


# Execute the `create_person` "unit of work" within a write transaction
session.execute_write(create_person, name="Michael")
```

  - If anything goes wrong within of the unit of work or there is a problem on Neo4j’s side, the transaction will be automatically rolled back and the database will remain in its previous state. If the unit of work succeeds, the transaction will be automatically committed.
  - Unlike session.run(), if a transient error is received by the driver, for example a connectivity issue with the DBMS, the driver will automatically retry the unit of work.

  - Manually creating transactions
  
``` python
with session.begin_transaction() as tx:
    # Run queries by calling `tx.run()`
```
  - have to manually commit or rollback
  
``` python
try:
    # Run a query
    tx.run(query, **params)

    # Commit the transaction
    tx.commit()
except:
    # If something goes wrong in the try block,
    # then rollback the transaction
    tx.rollback()
```

  - closing a session: session.close()
  
  - working example
  
``` python
# Create a Person node in the customers database

def create_person_work(tx, name):
    return tx.run("CREATE (p:Person {name: $name}) RETURN p",
        name=name).single()

def create_person(name):
    # Create a Session for the `people` database
    session = driver.session(database="people")

    # Create a node within a write transaction
    record = session.execute_write(create_person_work,
                                    name=name)

    # Get the `p` value from the first record
    person = record["p"]

    # Close the session
    session.close()

    # Return the property from the node
    return person["name"]
```

## Starting again
Wed Feb 28 2024

- Basic Stuff

- Creds
  - neo4j creds in original doc

- creating driver instance

``` text
driver = GraphDatabase.driver(
  connectionString, // (1)
  auth=(username, password), // (2)
  **configuration // (3)
)
```

- optional driver config eg

``` text
GraphDatabase.driver(uri, auth=auth,
    max_connection_lifetime=30 * 60,
    max_connection_pool_size=50,
    connection_acquisition_timeout=2 * 60)
```

- right conn string

``` text
You can verify the encryption level of your DBMS by checking the dbms.connector.bolt.enabled key in neo4j.conf.

If you are connecting to a DBMS hosted on Neo4j Aura, you will always use the neo4j+s scheme.
```

- Verify the connection details
  - driver.verify_connectivity()
  

- Code Challenge #1
  - https://graphacademy.neo4j.com/courses/app-python/1-driver/3-connecting/
  - this where gitpod should be started, a new workspace is created
  - earlier links are just for experimenting and not really useful
  - ws: https://neo4jgraphaca-apppython-njktjkneb2i.ws-us108.gitpod.io/
  
  - init driver code
    - locally switch code branch to 01-connect-to-neo4j
	- solution is there to copy
	
  - run test
    - pytest tests/01_connect_to_neo4j__test.py
	- 4 tests ran
	
  - neo4j creds are stored in env
    - created dir pkn
	- printenv > pkn/ws-env.txt
	
## Building Neo4j Applications with Python contd
Wed Feb 21 2024 

- Neo4j python driver
  - https://graphacademy.neo4j.com/courses/app-python/1-driver/1-about/
  - install on gitpod: pip install neo4j
  

## Building Neo4j Applications with Python
Wed Feb 21 2024

- Important

  - the course about coding using gitpod as the dev env
  - it is a flask app
  - based on the movies/reccomendations dataset

- Setup
  - https://graphacademy.neo4j.com/courses/app-python/0-setup/1-setup/
  
  - Creds:
    - neo4j creds in original doc
	
  - Accessing creds

``` text
import os

NEO4J_URI=os.getenv('NEO4J_URI')
NEO4J_USERNAME=os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD=os.getenv('NEO4J_PASSWORD')
```

  - running locally
    - https://github.com/neo4j-graphacademy/app-python
	- cloned: /Store/DEV/Neo4j/Academy$ gclone.sh https://github.com/neo4j-graphacademy/app-python
  
``` text
NEO4J_URI=bolt://{sandbox_ip}:{sandbox_boltPort}
NEO4J_USERNAME={sandbox_username}
NEO4J_PASSWORD={sandbox_password}
```

  - Gitpod
    - https://gitpod.io/user/account 
    - the lesson uses gitpod
    - logged int using Github, 2FA reqd
	- received message that an Oauth creds had been added to Github
    - can be used with pycharm
	  - needs some plugins in Pycharm
	- using browser in a separate window
	- installs base env from requirements.txt
		
