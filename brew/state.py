import time
import threading
import fysom
import logging


log = logging.getLogger(__name__)


class Machine(object):
    def __init__(self, controller, autopilot=True):
        state_table = {'initial': 'preparing',
                       'events': [{'name': 'heat', 'src': ['preparing', 'waiting', 'resting'], 'dst': 'heating'},
                            {'name': 'wait', 'src': ['heating', 'resting'], 'dst': 'waiting'},
                            {'name': 'rest', 'src': ['waiting', 'heating'], 'dst': 'resting'},
                            {'name': 'finish', 'src': ['waiting', 'resting'], 'dst': 'done'},
                            {'name': 'reset', 'src': 'finish', 'dst': 'preparing'}]}

        self._fsm = fysom.Fysom(state_table)
        self._steps = []
        self._autopilot = autopilot
        self._controller = controller
        self._thread = None
        self._exit_event = threading.Event()
        self.current_step = None

    def in_progress(self):
        return self._fsm.current != 'preparing'

    def append_step(self, step):
        self._steps.append(step)

    def heat(self, target_temperature):
        log.info("Heating to {} degC".format(target_temperature))
        current_temperature = self._controller.get_temperature()
        self._controller.set_temperature(target_temperature)

        while abs(target_temperature - current_temperature) > 1.0:
            if self._exit_event.wait(5):
                return

            current_temperature = self._controller.get_temperature()

    def start(self):
        def run_in_background():
            for step in self._steps:
                self.current_step = step

                # Heat first
                if not self._exit_event.is_set():
                    step['state'] = 'heat'
                    self._fsm.heat()
                    self.heat(step['temperature'])

                # Rest some time
                step['state'] = 'rest'
                self._fsm.rest()
                self._exit_event.wait(step['time'] * 60)

                step['state'] = 'done'

            if not self._exit_event.is_set():
                self.current_step = None
                self._fsm.finish()

        self._thread = threading.Thread(target=run_in_background)
        self._thread.start()

    def stop(self):
        self._exit_event.set()
        self._thread.join()
