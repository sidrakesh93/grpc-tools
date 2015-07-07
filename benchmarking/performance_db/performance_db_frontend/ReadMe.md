# Performance database front-end

This folder contains the source code for the web front-end of the performance database service, for diplaying user test metrics such as Queries Per Seconds (QPS), Percentile Latencies, Server and Client times, etc., and has been implemented using [Django](https://www.djangoproject.com/) and [Bootstrap](http://getbootstrap.com/).

The front end can display four types of pages, including:
* **Performance database table page**: The database table for displaying the performance metrics. It has been implemented using [Bootstrap table](https://github.com/wenzhixin/bootstrap-table). It supports features for searching and sorting on the columns, as well as displaying or hiding columns as per our requirement. It displays:
  * _User name_: Name of the user who submits this test result
  * _Timestamp_: Time when the databse received the data fron the user
  * _Test_: Name of the test
  * _Queries per seconds (QPS)_
  * _QPS per core_
  * _50th Percentile Latency (in μs)_
  * _90th Percentile Latency (in μs)_
  * _95th Percentile Latency (in μs)_
  * _99th Percentile Latency (in μs)_
  * _99.9th Percentile Latency (in μs)_
  * _Server system time percentage_
  * _Server user time percentage_
  * _Client system time percentage_
  * _Client user time percentage_

![alt tag](../images/Performance%20Database%20Table.png)


* **User statistics page**: The user statistics page can be accessed by clicking the hyperlinked name of the user in the performance database table page. The user statistics are displayed using 5 line charts, each plotting the value of particular metrics against time. The line charts are generated using the [Google charts API](https://developers.google.com/chart/interactive/docs/gallery/linechart). These line charts indicate how the different performance metrics vary for the user over time, in a specified time frame. The time frame is determined using [Date range picker](https://github.com/dangrossman/bootstrap-daterangepicker). The charts include:
  * _Queries per second (QPS) chart_
  * _QPS per core chart_
  * _Percentile latencies chart_
  * _Server times chart_: Plots the server system time and server user time.
  * _Client times chart_: Plots the client system time and client user time.

![alt tag](../images/User%20plots%20page.png)


* **General statistics page**: The general statistics page displays the Histograms for various performance metrics, using the performance data for all the users in a given time frame. The histograms are generated using the [Google charts API](https://developers.google.com/chart/interactive/docs/gallery/histogram), while the time range is implemented using [Date range picker](https://github.com/dangrossman/bootstrap-daterangepicker). Each performance metric is displayed on a different general statistics page.

![alt tag](../images/General%20statistics%20page.png)


* **Configurations page**: The configurations page can be accessed by clicking the hyperlinked test name in the performance database table, or by clicking the data points in the user plots. This page contains the test configuration information, which include the Client and Server configurations. It also contains the user system specifications, at the time of submitting the test results.

![alt tag](../images/Configs%20page.png)
