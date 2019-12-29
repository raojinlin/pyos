import types

from pyos import system_call


class Task(object):
    taskid = 0

    def __init__(self, target, sendval=None):
        Task.taskid += 1
        self.tid = Task.taskid
        self.target = target
        self.sendval = sendval
        self.stack = []

    def run(self):
        while True:
            try:
                result = self.target.send(self.sendval)
                if isinstance(result, system_call.SystemCall):
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



