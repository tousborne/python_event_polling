Simple prototype of event driven python thread synchronization.


The prototype is divided into the following threads:

* Polling thread that checks for work on a poll event
* Executor thread that "executes" any available work on a ready event
* Main thread manages a timer to kick off poll events and signals


The general flow of work is:

* When a "poll" event occurs, poll for instructions
	* Add any instructions to the instructions queue
	* Create a "ready" event
* When a "ready" event occurs, pull an instruction from the queue and execute it
	* If the instruction executes successfully, create a "poll" event.
* Create a "poll" event on a regular interval.  The poll events have to come from somewhere.
