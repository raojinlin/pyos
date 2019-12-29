import select
import queue

from pyos import system_call
from pyos import task


class Scheduler(object):
    def __init__(self):
        self.ready = queue.Queue()
        self.taskmap = {}
        self.exit_waiting = {}
        self.read_waiting = {}
        self.write_waiting = {}

    def new(self, target):
        newtask = task.Task(target)
        self.taskmap[newtask.tid] = newtask
        self.schedule(newtask)

        return newtask.tid

    def schedule(self, task):
        self.ready.put(task)

    def exit(self, task):
        print("Task %d terminated" % task.tid)
        for task in self.exit_waiting.pop(task.tid, []):
            self.schedule(task)

    def wait_for_exit(self, task, wait_tid):
        if wait_tid in self.taskmap:
            self.exit_waiting.setdefault(wait_tid, []).append(task)
            return True
        return False

    def io_task(self):
        while True:
            if self.ready.empty():
                self.io_poll(None)
            else:
                self.io_poll(0)
            yield

    def io_poll(self, timeout):
        if self.read_waiting or self.write_waiting:
            r, w, e = select.select(self.read_waiting, self.write_waiting, [], timeout)
            for fd in r:
                self.schedule(self.read_waiting.pop(fd))
            
            for fd in w:
                self.schedule(self.write_waiting.pop(fd))

    def wait_for_read(self, task, fd):
        self.read_waiting[fd] = task

    def wait_for_write(self, task, fd):
        self.write_waiting[fd] = task

    def mainloop(self):
        self.new(self.io_task())
        while self.taskmap:
            task = self.ready.get()
            try:
                result = task.run()
                if isinstance(result, system_call.SystemCall):
                    result.task = task
                    result.sched = self
                    result.handle()
                    continue

            except StopIteration:
                self.exit(task)
                continue

            self.schedule(task)

