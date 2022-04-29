from threading import Thread
import random
import time

class Stabilize(Thread):

    def __init__(self, node):
        Thread.__init__(self)
        self.node = node

    def run(self):
        while True:
            low = 1
            high = 5
            sleep_time = random.randint(2, 5)
            time.sleep(sleep_time)

            #Ping successor to see his predecessor if it's matching with current node
            succ_pred_id, succ_pred_ip = self.node.get_successors_predecessor()

