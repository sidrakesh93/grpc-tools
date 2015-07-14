# Authentication Server

The authentication server is responsible for creating an authenticated record of the user, based on the user's credentials and username, and to confirm a user's authentication status. The steps for this mechanism are as follows:

- The server receives user credentials and username from a user running the [test script](../../performance_db_script/run_perf_db_test.py), and uses the credentials for obtaining the user's Google Plus id using the [Google OAuth 2.0 protocol](https://developers.google.com/identity/protocols/OAuth2) and [OAuth 2.0 Python API](https://developers.google.com/api-client-library/python/guide/aaa_oauth).

- The server checks if the username passed by the user is available (if it has not already been assigned to him). If it is, the requested username is assigned to the user. This username-id mapping resolution is accomplished by the means of two maps, a _hashed id to username_ map and a _username to hashed id_ map. The maps are stored using [LevelDB](http://leveldb.org/). The client is then sent an acknowledgement message for moving forward with sending the data to the database server.

- If the username requested by is not unique, nor has been assigned to him earlier, the client is sent an error message, and the user is asked to provide a new username. The new username and credentials of the user are re-sent to the server for authenticating the user. This process is repeated till a unique username is not assigned to the user.

- The client moves forward with sending the performance data as well as the _hashed user id_ to the [performance database server](../data_server). The performance database server sends the received _hashed user id_ to the authentication server. The username of the user is looked up using the _hashed id to username_ map.

- If no entry can be found in this map for the passed hashed id, it implies that the user did not perform the earlier steps of authentication and an error message is sent to the performance database server. However, if the entry is found, an acknowledgement is sent to the performance database server as an authentication confirmation for the user.

The authentication server is a Python script, _auth_server.py_, and can be passed the following command-line parameters:

- Port of the server (`--port`).
- Location of the id to username database (`--id_name_db`).
- Location of the username to id database (`--name_id_db`).

A typical command to run the server would look like:

    ./auth_server.py --port=2817 --id_name_db=$HOME/.grpc/id_name --name_id_db=$HOME/.grpc/name_id
