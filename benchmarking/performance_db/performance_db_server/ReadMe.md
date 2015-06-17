# Performance database server

The performance database server, implemented in C++, acts as the central coordinator for the clients submitting their data for the QPS tests, as well for providing data to the frontend which display this data. It is responsible for:

* Collecting performance metrics data such as Queries Per Second (QPS), Percentile Latencies, Server and Client times, etc. from the clients and writing them to a database. The database has been implemented using [LevelDb](http://leveldb.org/).

* Storing the users' data with their profile information, which is obtained using the access tokens provided by the client while submitting their test results.

* Providing the web front-end (implemented using [Django](https://www.djangoproject.com/)) with data retrieved from the database.
