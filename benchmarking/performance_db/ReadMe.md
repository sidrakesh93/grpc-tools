# Performance Database Tool

This folder contains the source code for the server and front-end of the authenticated performance database tool.

The authenticated performance database tool has been developed with the objective of collecting and displaying test results of the QPS tests for authenticated users.

Broadly speaking, the tool collects and displays various performance metrics, including Queries Per Second (QPS), QPS per core, Percentile Latencies (50<sup>th</sup>, 90<sup>th</sup>, 95<sup>th</sup>, 99<sup>th</sup> and 99.9<sup>th</sup>), server system time, server user time, client system time and client user time. Apart from these, the tool also collects user specific data, such as the user’s personal information (obtained from his/her Google+ profile), and the user’s system information (such as the Architecture, Processor, etc.).

More formally, the objectives of the performance database tool can be represented as:

* Collecting the QPS test results from the users and sending them to a server.
* Providing a server to receive data from the users, and to provide data to the web front-end.
* Displaying the data in a convenient web front end, with multiple options to analyze the data.
