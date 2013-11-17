import time
import threading
import fysom
import logging


log = logging.getLogger(__name__)


class HeatChange(object):
    def __init__(self, controller, temperature):
        self.controller = controller
        self.temperature = temperature

    def do(self, fsm, exit_event):
        log.info("Heating to {} degC".format(self.temperature))
        fsm.heat()
        target_temperature = self.temperature
        current_temperature = self.controller.get_temperature()
        self.controller.set_temperature(target_temperature)

        while abs(target_temperature - current_temperature) > 1.0:
            if exit_event.wait(5):
                return

            current_temperature = self.controller.get_temperature()


class Rest(object):
    def __init__(self, duration):
        self.duration = duration

    def do(self, fsm, exit_event):
        log.info("Sleeping for {} minutes".format(self.duration))
        fsm.rest()
        exit_event.wait(self.duration * 60)


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

    def in_progress(self):
        return self._fsm.current != 'preparing'

    def append_heat_change(self, temperature):
        self._steps.append(HeatChange(self._controller, temperature))

    def append_rest(self, duration):
        self._steps.append(Rest(duration))

    def start(self):
        def run_in_background():
            for step in self._steps:
                if not self._exit_event.is_set():
                    step.do(self._fsm, self._exit_event)

            if not self._exit_event.is_set():
                self._fsm.finish()

        self._thread = threading.Thread(target=run_in_background)
        self._thread.start()

    def stop(self):
        self._exit_event.set()
        self._thread.join()
