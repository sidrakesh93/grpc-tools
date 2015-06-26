# Performance database server

The performance database server, implemented in C++, acts as the central coordinator for the clients submitting their data for the QPS tests, as well for providing data to the frontend which display this data. It is responsible for:

* Collecting performance metrics data such as Queries Per Second (QPS), Percentile Latencies, Server and Client times, etc. from the clients and writing them to a database. The database has been implemented using [LevelDb](http://leveldb.org/), an open-source, light-weight, single-purpose library for persistence with bindings to many platforms.

* Storing the users' data with their profile information, which is obtained using the access tokens provided by the client while submitting their test results.

* Providing the web front-end (implemented using [Django](https://www.djangoproject.com/)) with data retrieved from the database.

Upon receiving data from the user, the server uses the received access token to obtain the user’s personal details using the [OAuth 2.0 protocol](https://developers.google.com/identity/protocols/OAuth2). [Libcurl](http://curl.haxx.se/) is used to handle the web requests.

The server timestamps the received data, and stores it to the database along with the user’s information. Leveldb is a key-value storage database; here the key is chosen as a unique ID number which Google assigns to each user in their Google+ profile information. The user’s information is not replicated: it is updated if the user’s information has changed, and is stored in only one place in the database.

The frontend makes two types of calls to the server: to obtain the data either for one user or for all the users. The server sends data to the frontend accordingly.

The server is started using a Python wrapper, _run_perf_db_server.py_, needs to be passed the address in _hostname:port_ format and the location of the database as commandline arguments. The user needs to run `make` before using the server with the Python wrapper, to generate the necessary binaries. The command to run the server will typically look like:

    ./run_perf_db_server --address=hostname:port --database=path_to_database
