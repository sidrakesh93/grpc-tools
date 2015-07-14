# Performance Database Tool

The authenticated performance database tool has been developed with the objective of collecting and displaying test results of the QPS tests for authenticated users.

Broadly speaking, the tool collects and displays various performance metrics, including Queries Per Second (QPS), QPS per core, Percentile Latencies (50<sup>th</sup>, 90<sup>th</sup>, 95<sup>th</sup>, 99<sup>th</sup> and 99.9<sup>th</sup>), server system time, server user time, client system time and client user time. Apart from these, the tool also collects user specific data, such as the user’s system information (such as the Architecture, Processor, etc.).

More formally, the objectives of the performance database tool can be represented as:

* Authenticating the user based on his Google account credentials.
* Collecting the QPS test results from the users and sending them to a server.
* Providing a server to receive data from the users, and to provide data to the web front-end.
* Displaying the data in a convenient web front end, with multiple options to analyze the data.

[performance_db_script](performance_db_script/) contains the script required by the user who wishes to submit the test results to the performance database. [This](performance_db_script/ReadMe.md) contains information about the script and how to use it.

[performance_db_server](performance_db_server/) contains the code and scripts for the Authentication server and the Database server. Information and instructions on how to use them can be found [here](performance_db_server/auth_server/ReadMe.md) and [here](performance_db_server/data_server/ReadMe.md) respectively.

[performance_db_frontend](performance_db_frontend/) contains the code for the web frontend (implemented using [Django](https://www.djangoproject.com/)). Further information can be found [here](performance_db_frontend/ReadMe.md).

Both the Authentication server and the Performance database server must be set running for the user to be able to submit his results using the script. Currently, the users must run their own servers. Public servers to collect data from the users shall be available shortly.
