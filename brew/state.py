import time
import threading
import fysom
import logging


log = logging.getLogger(__name__)


class Machine(object):
    def __init__(self, controller):
        state_table = {'initial': 'preparing',
                       'events': [{'name': 'heat', 'src': ['preparing', 'waiting', 'resting'], 'dst': 'heating'},
                            {'name': 'wait', 'src': ['heating', 'resting'], 'dst': 'waiting'},
                            {'name': 'rest', 'src': ['waiting', 'heating'], 'dst': 'resting'},
                            {'name': 'finish', 'src': ['waiting', 'resting'], 'dst': 'done'},
                            {'name': 'reset', 'src': 'finish', 'dst': 'preparing'}],
                       'callbacks': {
                            'onheat': self.on_heat,
                            'onrest': self.on_rest
                       }}

        self.fsm = fysom.Fysom(state_table)
        self._controller = controller
        self._threads = []
        self._exit_request = False

    def in_progress(self):
        return self.fsm.current != 'preparing'

    def stop(self):
        self._exit_request = True

        for thread in self._threads:
            thread.join()

        self._exit_request = False

    def on_heat(self, event):
        def heat():
            log.info("Heating to {} degC".format(event.temperature))
            target_temperature = event.temperature
            current_temperature = self._controller.get_temperature()
            self._controller.set_temperature(target_temperature)

            while abs(target_temperature - current_temperature) > 1.0 and not self._exit_request:
                time.sleep(5)
                current_temperature = self._controller.get_temperature()
                log.info("Current temperature {}".format(current_temperature))

            event.fsm.wait()

        thread = threading.Thread(target=heat)
        self._threads.append(thread)
        thread.start()

    def on_rest(self, event):
        def rest():
            print("sleeping for {} minutes".format(event.duration))
            time.sleep(event.duration * 60)
            event.fsm.wait()

        thread = threading.Thread(target=rest)
        self._threads.append(thread)
        thread.start()
