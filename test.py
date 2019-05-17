import mode
from mode import Service

class SimplePoller(Service):
    @Service.timer(1.0)
    async def poll(self) -> None:
        self.log.info('poll')

    @Service.task
    async def _background_task(self) -> None:
        self.log.info('BACKGROUND TASK STARTING')
        while not self.should_stop:
            await self.sleep(3.0)
            self.log.info('BACKGROUND SERVICE WAKING UP')

if __name__ == '__main__':
    from mode import Worker
    Worker(SimplePoller(), loglevel="info").execute_from_commandline()
