# Cluster Performance Watcher
The Project files watch the CPU and MEM usage of every user and process in one instance of ```top```
What this does is keep track of the average and past 3 values every time the command is called.

What is happening inside ```watcher.py```:
  1. When ```top``` is called every 5 seconds, we store those values, and it is called for a total of 30s
  2. We then keep track of the past three values at the end of every 30s, along with the Average CPU and MEM values for every   user and every process, as well as the maximum value in those 30s, again for every user and every process.
  3. Finally, this entire process is repeated every 30s, for a total duration fo 90s, and at the end of every 90s we have the 
  params as described above. 
  4. All the data described above is stored on a MYSQL Database, in the form of several tables (2 tables for every 5s data,     and a historical table for the every 90s data)
  5. The historical data is used to plot graphs (using Grafana) for all users' and process' CPU and MEM data (Average)

All the times mentioned above configurable, in the form of varibles.

Furthermore, the count sequence is maintained quite simply in a SQL database and is incremented every time the ```top``` command is called so as to correctly maintain the average data.

We can also get a flame graph by running the command ```py-spy --flame profile.svg -- python3 watcher.py```. These yields a flame graph as below. An SVG File is a scalable vector graph, something like a screenshot of a system process. This collects 200 samples in the program, and each process/subprocess is graphed. 


The ```.svg``` file can be opened in a web browser and then we can actually visualize,in detail, all the processes that are going on. ```.svg``` is actually ```XML``` encoded, so that enables this 'screenshot' to work something like a website
 
 Other files:
 
     1. `ssh_conf.py`- contains the SSH connect function
     2. `sql_conf.py`- contains the SQL operations
     (The above two files aren't included in the repo)
     3. `ssh_exec.py`- contains the SSH functions to be executed in the main.py file
     4. `sql_exec.py` - contains the SQL functions to be executed in the main.py file
