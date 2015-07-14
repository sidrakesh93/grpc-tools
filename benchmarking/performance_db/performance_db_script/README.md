# Performance Database Script

This folder contains the script required for authenticating the user, collecting the performance metrics from the user and reporting them to the performance database.

### Collecting the QPS test results from the users

The results are collected from the users by the means of a derived reporting class, the _PerfDbReporter_,  in the [QPS test](https://github.com/grpc/grpc/tree/master/test/cpp/qps) reporter, which is responsible for sending data the the running backend server via RPC calls (implemented using gRPC). The implementation for this mechanism is in C++. The UserDatabaseReporter class makes use of a separate class, _PerfDbClient_, which directly interacts with the server.

The authenticated performance reporting tool is initiated using the Python wrapper, _run_perf_db_test.py_, which subsequently begins the actual test. Before the actual QPS test begins, the user is authenticated using the [OAuth 2.0 protocol](https://developers.google.com/identity/protocols/OAuth2), and system and network information is collected.

The user must pass the following as commandline arguments to the script:
- The path of the test which the user wishes to run (`--test`).
- The username of the user (`--username`).

The user may optionally pass the following as commandline arguments:
- A custom 'tag' for the test (`--tag`).
- The location of the user credentials directory (`--creds_dir`).
- The location of the client secrets file (`--clients_secrets`).
- The address of the performance database server (`--data_server_addr`).
- The address of the authentication server (`--auth_server_addr`).

A typical command to send the data to the performance database server could look like:

    ./run_perf_db_test.py --test=path_to_test --username=your_username --tag='Custom tag' --creds_dir=$HOME/.grpc/credentials --client_secrets=client_secrets.json --data_server_addr=server_host --auth_server_addr=auth_host

We now briefly describe the authentication process.

#### Authentication

The tool uses [OAuth 2.0 protocol](https://developers.google.com/identity/protocols/OAuth2) and the [OAuth 2.0 Python API](https://developers.google.com/api-client-library/python/guide/aaa_oauth) for authentication and authorization. If the user is running the test for the first time on his/her system, or his/her credentials have been removed from his system or are invalid, he/she will be prompted to authenticate in the browser, which shall open automatically.

    sidrakesh@sidrakesh:~/work/grpc-tools/benchmarking/performance_db/performance_db_script$ python run_perf_db_test.py --test=/usr/local/google/home/sidrakesh/work/grpcnew/grpc/bins/opt/async_streaming_ping_pong_test --username=sidrakesh
    Your browser has been opened to visit:
    
        https://accounts.google.com/o/oauth2/auth?scope=email+profile&redirect_uri=http%3A%2F%2Flocalhost%3A8080%2F&response_type=code&client_id=1018396037782-tv81fshn76nemr24uuhuginceb9hni2m.apps.googleusercontent.com&access_type=offline
    
    If your browser is on a different machine then exit and re-run this
    application with the command-line parameter 
    
      --noauth_local_webserver
    
    Created new window in existing browser session.


In the browser, the user needs to login (if not already logged in), and is asked to accept the terms of agreement as shown:

![alt tag](../images/Auth%20agreement.png)

followed by a confirmation message:

![alt tag](../images/Auth%20completion.png)

The credentials of the user are stored in a file following this authentication. The file contents are then sent to the *Authentication Server* alongwith the username of the user to register the user as an authenticated one. The authentication server is described in detail in 'performance_db_server/auth_server/ReadMe'. The test resumes after this step.

#### Sending data

Following the authentication, the system information of the user is collected using the Python script. The specs include CPU(s), Socket(s), CPU Family, Cache information, etc., as well as network information including NIC speeds and Inet addresses, as well as the TCP_RR transmission rate per second. This information is passed as an argument to the test, as it needs to be sent alongwith the test results.

In addition to the already present _LogReporter_, the _PerfDbReporter_ corresponding to the tool records information in parallel to the _LogReporter_, and upon completion sends the hashed user id, system information and test results to the listening data server. The hashed id is used as a key in the database for the user.
