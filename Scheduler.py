"""

This project was constructed by Justin Adams using David Beazley's
lecture slides on A Curious Course on Coroutines and Concurrency.
Copyright (C) 2009, All Rights Reserved, By David Beazley
Presented at PyCon 2009, March 25, 2009.
This information has since been released underneath the Creative Commons licenses.
Find out more about this license here: https://creativecommons.org/licenses/

An additional copyright is placed on the differential of this codebase,
which is a modified implementation of David Beazley's work using optimization
solutions from the following works:

Section 1: Scheduling Problem Classical Optimization Algorithms


Section 2: Quantum Algorithms Related to VQE Solutions to the scheduling Problem


Section 3: Variational Quantum Eigensolver Configurations


Section 4: Variational Quantum System Hardware


Copyright (C) 2020, All Rights Reserved, By Justin Adams

The goal of this forked implementation of David Beazley's project is to classify
the algorithms and quantify the number of qubits required to prove Quantum Supremacy
for the scheduling problem using different Variational Quantum Eigensolver (VQE)
implementations. Benchmarking will determine when Quantum Supremacy occurs in
the domain of the scheduling problem NP-Complete space. When the system performance
of the (VQE) exceeds the classical algorithm's maximum efficiency with all known
optimizations applied to this code base, then Quantum Supremacy for scheduling Problems
can be declared and a paper documenting this solution may accompany this codebase.
"""
import select

from Promise_Architecture import Task, NewTask, GetTid, WaitTask, KillTask
from EchoServer import server, server_improved, server_final
from queue import Queue
from SystemCall import SystemCall


class Scheduler(object):
    # Add class comment
    def __init__(self):
        # Add init comment
        self.ready = Queue()
        self.taskmap = {}
        self.read_waiting = {}
        self.write_waiting = {}
        self.exit_waiting = {}

    def new(self, target):
        # Add new function comment
        newtask = Task(target)
        self.taskmap[newtask.tid] = newtask
        self.schedule(newtask)
        return newtask.tid

    def loop_one(self):
        while self.taskmap:
            task = self.ready.get()
            task.run()
            self.schedule(task)

    def crash(self):
        # Add crash function comment
        while self.taskmap:
            task = self.ready.get()
            task.run()
            self.schedule(task)

    def loop_three(self):
        while self.taskmap:
            task = self.ready.get()
            try:
                task.run()
            except StopIteration:
                self.exit(task)
                continue
            self.schedule(task)

    def loop_four(self):
        while self.taskmap:
            task = self.ready.get()
            try:
                task.run()
            except StopIteration:
                self.exit(task)
                continue
            self.schedule(task)

    def mainloop(self):
        # Add mainloop function comment
        while self.taskmap:
            task = self.ready.get()
            try:
                result = task.run()
                if isinstance(result, SystemCall):
                    result.task = task
                    result.schedule = self
                    result.handle()
                    continue
            except StopIteration:
                self.exit(task)
                continue
            self.schedule(task)

    def mainloop_os(self):
        # Add mainloop function comment
        while self.taskmap:
            task = self.ready.get()
            try:
                result = task.run()
                if isinstance(result, SystemCall):
                    result.task = task
                    result.schedule = self
                    result.handle()
                    continue
            except StopIteration:
                self.task_waiting_exit(task)
                continue
            self.schedule(task)

    def mainloop_os_io(self):
        # Add mainloop function comment
        self.new(self.io_task())
        while self.taskmap:
            task = self.ready.get()
            try:
                result = task.run()
                if isinstance(result, SystemCall):
                    result.task = task
                    result.schedule = self
                    result.handle()
                    continue
            except StopIteration:
                self.task_waiting_exit(task)
                continue
            self.schedule(task)

    def schedule(self, task):
        # Add schedule function comment
        self.ready.put(task)

    def io_task(self):
        while True:
            if self.ready.empty():
                self.io_poll(None)
            else:
                self.io_poll(0)
            yield

    def io_poll(self, timeout):
        if self.read_waiting or self.write_waiting:
            r, w, e = select.select(self.read_waiting,
                                    self.write_waiting, [], timeout)
            for fd in r:
                self.schedule(self.read_waiting.pop(fd))
            for fd in w:
                self.schedule(self.write_waiting.pop(fd))

    def exit(self, task):
        # Add exit function comment
        print("Task %d terminated." % task.tid)
        del self.taskmap[task.tid]

    def task_waiting_exit(self, task):
        print("Task %d terminated" % task.tid)
        del self.taskmap[task.tid]
        # Notify other tasks waiting for exit
        for task in self.exit_waiting.pop(task.tid, []):
            self.schedule(task)

    def wait_for_read(self, task, fd):
        self.read_waiting[fd] = task

    def wait_for_write(self, task, fd):
        self.write_waiting[fd] = task

    def wait_for_exit(self, task, waittid):
        if waittid in self.taskmap:
            self.exit_waiting.setdefault(waittid, []).append(task)
            return True
        else:
            return False


if __name__ == "__main__":
    # Add test suite comment.
    USER_INTERFACE = "Coroutine and Concurrency test suite.\n" \
                "Press enter at any time to exit a test.\n" \
                "1. Running tasks infinitely in a scheduler.\n" \
                "2. Crashing tasks without exception handling.\n" \
                "3. Prevent crashing with StopIteration exception handling.\n" \
                "4. Operating System emulation to allow task scheduling.\n" \
                "5. Operating System emulation with parent child task handoff.\n" \
                "6. Server operating system emulation.\n" \
                "7. Server with promise based multi-tasking.\n" \
                "8. Promise based socket server instance(s) with promise based multi-tasking.\n" \
                "Please enter a test number: "

    def foo():
        # Add foo function comment
        my_task_id = yield GetTid()
        while True:
            print("I'm foo", my_task_id)
            yield
            
    def foo_five():
        for i in range(5):
            print("I'm Foo")
            yield

    def bar():
        # Add bar function comment
        my_task_id = yield GetTid()
        while True:
            print("I'm bar", my_task_id)
            yield

    def simple_foo():
        # Add simple_foo function comment
        while True:
            print("I'm foo")
            yield

    def simple_bar():
        # Add simple_bar function comment
        while True:
            print("I'm bar")
            yield

    def pity_foo():
        for i in range(10):
            print("I'm foo")
            yield


    def pity_bar():
        for i in range(5):
            print("I'm bar")
            yield


    def id_foo():
        my_task_id = yield GetTid()
        for i in range(5):
            print("I'm foo", my_task_id)
            yield


    def id_bar():
        my_task_id = yield GetTid()
        for i in range(10):
            print("I'm bar", my_task_id)
            yield


    def main():
        child = yield NewTask(id_foo())
        for i in range(5):
            yield
        yield KillTask(child)
        print("Main done.")

    def main_os():
        child = yield NewTask(id_foo())
        print("Waiting for child")
        yield WaitTask(child)
        print("Child done")

    def alive():
        while True:
            print("I'm alive!")
            yield

    while True:
        test = input(USER_INTERFACE)
        schedule = None
        if isinstance(test, str) and test != '':
            test = int(test)
            # 1. Running tasks infinitely in a scheduler.
            if test == 1:
                schedule = Scheduler()
                schedule.new(simple_foo())
                schedule.new(simple_bar())
                schedule.loop_one()
            # 2. Crashing tasks without exception handling.
            elif test == 2:
                schedule = Scheduler()
                schedule.new(pity_foo())
                schedule.new(bar())
                schedule.crash()
            # 3. Prevent crashing with StopIteration exception handling.
            elif test == 3:
                schedule = Scheduler()
                schedule.new(pity_foo())
                schedule.new(pity_bar())
                schedule.loop_three()
            # 4. Adding system call interrupts to manage multitasking.
            elif test == 4:
                schedule = Scheduler()
                schedule.new(main())
                schedule.mainloop()
            # 5. Adding additional functionality
            elif test == 5:
                schedule = Scheduler()
                schedule.new(main_os())
                schedule.mainloop_os()
            elif test == 6:
                schedule = Scheduler()
                schedule.new(alive())
                schedule.new(server(45000))
                schedule.mainloop_os_io()
            elif test == 7:
                schedule = Scheduler()
                schedule.new(alive())
                schedule.new(server_improved(45000))
                schedule.mainloop_os_io()
            elif test == 8:
                schedule = Scheduler()
                schedule.new(alive())
                schedule.new(server_final(45000))
                schedule.mainloop_os_io()
