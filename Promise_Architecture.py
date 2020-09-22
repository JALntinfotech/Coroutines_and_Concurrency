import types
from SystemCall import SystemCall


class Task(object):
    my_task_id = 0

    def __init__(self, target):
        Task.my_task_id += 1
        self.tid = Task.my_task_id
        self.target = target
        self.send_value = None
        self.stack = []

    def run(self):
        while True:
            try:
                result = self.target.send(self.send_value)
                if isinstance(result, SystemCall):
                    return result
                if isinstance(result, types.GeneratorType):
                    self.stack.append(self.target)
                    self.sendval = None
                    self.target = result
                else:
                    if not self.stack:
                        return
                    self.sendval = result
                    self.target = self.stack.pop()
            except StopIteration:
                if not self.stack:
                    raise
                self.sendval = None
                self.target = self.stack.pop()


class NewTask(SystemCall):
    # Add class comment
    def __init__(self, target):
        # Add init comment
        self.target = target

    def handle(self):
        # Add handle function comment
        tid = self.schedule.new(self.target)
        self.task.send_value = tid
        self.schedule.schedule(self.task)


class WaitTask(SystemCall):
    def __init__(self, tid):
        self.tid = tid

    def handle(self):
        result = self.schedule.wait_for_exit(self.task, self.tid)
        self.task.send_value = result
        # If waiting for a non-existent task,
        # return immediately without waiting
        if not result:
            self.schedule.schedule(self.task)


class KillTask(SystemCall):
    # Add class comment
    def __init__(self, tid):
        # Add init comment
        self.tid = tid

    def handle(self):
        # Add function comment
        task = self.schedule.taskmap.get(self.tid, None)
        if task:
            task.target.close()
            self.task.send_value: bool = True
        else:
            self.task.send_value: bool = False
        self.schedule.schedule(self.task)


class GetTid(SystemCall):
    # Add class comment
    def handle(self):
        # Add handle function comment
        self.task.send_value = self.task.tid
        self.schedule.schedule(self.task)


class ReadWait(SystemCall):
    def __init__(self, f):
        self.f = f

    def handle(self):
        fd = self.f.fileno()
        self.schedule.wait_for_read(self.task, fd)


class WriteWait(SystemCall):
    def __init__(self, f):
        self.f = f

    def handle(self):
        fd = self.f.fileno()
        self.schedule.wait_for_write(self.task, fd)


def accept(sock):
    yield ReadWait(sock)
    yield sock.accept()


def send(sock, buffer):
    while buffer:
        yield WriteWait(sock)
    len = sock.send(buffer)
    buffer = buffer[len:]


def receive(sock, maxbytes):
    yield ReadWait(sock)
    yield sock.recv(maxbytes)


if __name__ == "__main__":
    def foo():
        print("Part 1")
        yield
        print("Part 2")
        yield


    t1 = Task(foo())
    t1.run()
    t1.run()
