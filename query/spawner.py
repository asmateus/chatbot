import subprocess as sp
import sys
import os

from .bots import types


class Spawner:
    @staticmethod
    def spawn(types_to_spawn=types.ALL_QUERIES) -> '_RabbitConsumer':
        pids = []
        for t in types_to_spawn:
            pids.append(Spawner._start_subprocess(t))

        return pids

    @staticmethod
    def _start_subprocess(t):
        # Start consumer, pass type as parameter
        p = sp.Popen(
            ['python', '-m', 'bots.consumers', '-t', t],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stderr=sp.STDOUT,
        )

        # Display (or log?) PID for future kill
        print('Started consumer of type', t, 'with PID', p.pid)

        return p.pid


if __name__ == '__main__':
    Spawner.spawn()

    # Ensure immediate smooth exit
    sys.exit(0)
