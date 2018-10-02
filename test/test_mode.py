import mode
from mode import Service, OneForOneSupervisor


class SadPoller(Service):
    def __init__(self, name, *arg, **kwds):
        self.poller_name = name
        super().__init__(*arg, **kwds)

    @Service.timer(1.0)
    async def poll(self) -> None:
        self.log.info(f'{self.poller_name}... meh...')

    @Service.timer(3.0)
    async def too_much(self) -> None:
        await self.crash(ValueError(f'{self.poller_name}... this is too much...'))




class SimplePoller(Service):
    Supervisor = OneForOneSupervisor

    @Service.timer(1.0)
    async def poll(self) -> None:
        self.log.info('poll')

    # @Service.task
    # async def _background_task(self) -> None:
    #     self.log.info('BACKGROUND TASK STARTING')
    #     while not self.should_stop:
    #         await self.sleep(3.0)
    #         self.log.info('BACKGROUND SERVICE WAKING UP')

    async def on_first_start(self) -> None:
        self.log.info('Starting! Making a bernd!')
        self.sad_bernd = self.add_dependency(SadPoller('bernd'))
        self.supervisor = self.Supervisor()
        self.supervisor.add(self.sad_bernd)

    async def on_start(self) -> None:
        self.log.info('Starting Poller!!!')

    @Service.timer(8.0)
    async def no_key(self) -> None:
        await self.crash(KeyError(f'I cant find the key!!!'))


    # async def on_init_dependencies(self):
    #     return [SadPoller('bernd')]



class SimplePollerSupervisor(OneForOneSupervisor):
    ...



if __name__ == '__main__':
    from mode import Worker

    supervisor = OneForOneSupervisor()
    poller = SimplePoller()
    supervisor.add(poller)


    Worker(supervisor, loglevel="info").execute_from_commandline()
