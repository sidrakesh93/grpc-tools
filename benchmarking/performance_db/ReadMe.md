# Performance Database Tool

This folder contains the source code for the server and front-end of the authenticated performance database tool.

The authenticated performance database tool has been developed with the objective of collecting and displaying test results of the QPS tests for authenticated users.

Broadly speaking, the tool collects and displays various performance metrics, including Queries Per Second (QPS), QPS per core, Percentile Latencies (50<sup>th</sup>, 90<sup>th</sup>, 95<sup>th</sup>, 99<sup>th</sup> and 99.9<sup>th</sup>), server system time, server user time, client system time and client user time. Apart from these, the tool also collects user specific data, such as the user’s personal information (obtained from his/her Google+ profile), and the user’s system information (such as the Architecture, Processor, etc.).

More formally, the objectives of the performance database tool can be represented as:

* Collecting the QPS test results from the users and sending them to a server.
* Providing a server to receive data from the users, and to provide data to the web front-end.
* Displaying the data in a convenient web front end, with multiple options to analyze the data.

### Collecting the QPS test results from the users

The results are collected from the users by the means of a derived reporting class, the _PerfDbReporter_,  in the [QPS test](https://github.com/grpc/grpc/tree/master/test/cpp/qps) reporter, which is responsible for sending data the the running backend server via RPC calls (implemented using gRPC). The implementation for this mechanism is in C++. The UserDatabaseReporter class makes use of a separate class, _PerfDbClient_, which directly interacts with the server.

The authenticated performance reporting tool is initiated using a Python wrapper which subsequently begins the actual test. Before the actual PQS test begins, the user is authenticated using the [OAuth 2.0 protocol](https://developers.google.com/identity/protocols/OAuth2), and system and network information is collected.

Commandline arguments are handled using [python_gflags](https://code.google.com/p/python-gflags/). The user _must_ pass the path or name of the test which he/she wishes to run, and his/her gmail id as command-line arguments, and may optionally pass the address of the performance database server and location of the access tokens' directory. Superuser access could be required.

A typical command to send the data to the performance database server could look like:

    sudo ./run_perf_db_test.py --test=qps_test --email=username@gmail.com --tokens_dir=/usr/local/access_tokens --server_address=server_host

We now briefly describe the authentication process.

#### Authentication

The tool uses [OAuth 2.0 protocol](https://developers.google.com/identity/protocols/OAuth2) for authentication and authorization. If the user is is running the test for the first time on his/her system, or his/her refresh token has expired, he/she will be prompted to authorize the application using a code provided by the protocol, and his/her login credentials in a web browser. The authorization link will be displayed in the terminal.

![alt tag](https://github.com/sidrakesh93/grpc-tools/blob/master/benchmarking/performance_db/images/Auth%20terminal.png)

Upon following the verification URL, the user needs to login (if not already logged in), and then sees the following:

![alt tag](https://github.com/sidrakesh93/grpc-tools/blob/master/benchmarking/performance_db/images/Auth%20code.png)

and upon entering the code and continuing, the user is asked to accept the Terms of agreement as shown:

![alt tag](https://github.com/sidrakesh93/grpc-tools/blob/master/benchmarking/performance_db/images/Auth%20agreement.png)

followed by a confirmation message:

![alt tag](https://github.com/sidrakesh93/grpc-tools/blob/master/benchmarking/performance_db/images/Auth%20completion.png)

This marks the completion of authentication. The test resumes after a couple of seconds with the obtained access token as an argument.

The access and refresh tokens for the user are stored on his/her system. When the user runs the script again, his/her stored tokens are used and he does not need to authenticate again.

#### Sending data

Following the authentication, the system information of the user is collected using the Python script. The specs include CPU(s), Socket(s), CPU Family, Cache information, etc., as well as network information including NIC speeds and Inet addresses, as well as the TCP_RR transmission rate per second. This information is passed as an argument to the test, as it needs to be sent alongwith the test results.

In addition to the already present _LogReporter_, the _PerfDbReporter_ corresponding to the tool records information in parallel to the _LogReporter_, and upon completion sends the access token, system information and test results to the listening server.
