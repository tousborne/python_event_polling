#!/usr/bin/env python

import dataclasses
import queue
import random
import signal
import sys
import threading
import time


# Synchronization class
@dataclasses.dataclass
class Sync:
    stop: threading.Event = threading.Event()
    poll: threading.Event = threading.Event()
    ready: threading.Event = threading.Event()
    instructions: queue.Queue = queue.Queue()


POLL_INTERVAL = 10
SYNC = Sync()
EXIT = False


######################
# Instruction thread #
######################
def execute(name: str):
    # Take some time to "execute"
    time.sleep(random.expovariate(1))

    # 20% failure rate ... maybe.
    result = random.expovariate(1 / 5) > 1
    print('instruction {} executed: {}'.format(name, result))

    return result


def executor(sync: Sync):
    while sync.ready.wait():
        # Reset event.
        sync.ready.clear()

        while True:
            # Check for exit condition.
            if sync.stop.is_set():
                return

            # Try to get the next instruction in the queue
            try:
                name = sync.instructions.get(block=False)

            except queue.Empty:
                break

            result = execute(name)
            if result:
                sync.poll.set()


##################
# Polling thread #
##################
def poll():
    names = ['get', 'export', 'inquire', 'test']

    # 75% chance of having an instruction ... maybe.
    if random.expovariate(1 / 4) > 0:
        return names[random.randrange(len(names))]

    else:
        return ''


def poller(sync: Sync):
    while sync.poll.wait():
        # Reset the event.
        sync.poll.clear()

        # Check the exit condition.
        if sync.stop.is_set():
            return

        instr = poll()
        if instr:
            print('Polled {}'.format(instr))

            sync.instructions.put(instr)
            sync.ready.set()

        else:
            print('No instruction polled')


###############
# Main thread #
###############
def signal_handler(signum, frame):
    global EXIT

    if not EXIT:
        EXIT = True

        # Set the exit condition and wake all threads
        SYNC.stop.set()
        SYNC.poll.set()
        SYNC.ready.set()

        print('Shutting down gracefully!')

    else:
        print('Force exiting')
        sys.exit()


# Repeatedly set the given event every interval seconds
def repeat_event(interval: int, event: threading.Event, stop: threading.Event):
    while True:
        if stop.is_set():
            return

        if not event.is_set():
            print('timed poll')
            event.set()

        time.sleep(interval)


def main():
    global SYNC
    global POLL_INTERVAL

    signal.signal(signal.SIGINT, signal_handler)

    poll_thread = threading.Thread(target=poller, args=[SYNC])
    exec_thread = threading.Thread(target=executor, args=[SYNC])

    poll_thread.start()
    exec_thread.start()

    repeat_event(POLL_INTERVAL, SYNC.poll, SYNC.stop)

    poll_thread.join()
    exec_thread.join()


if __name__ == '__main__':
    signal
    main()
