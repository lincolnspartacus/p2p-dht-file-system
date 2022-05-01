from threading import Thread
import random
import time
import utils

class Stabilize(Thread):

    def __init__(self, node):
        Thread.__init__(self)
        self.node = node

    def run(self):
        while True:
            low = 3
            high = 6
            sleep_time = random.randint(low, high)
            time.sleep(sleep_time)

            #Ping successor to see his predecessor if it's matching with current node
            try:
                x_id, x_ip = self.node.get_successors_predecessor()
                print('[stabilize] {}: Predecessor {} Successor {}'.format(self.node.id, self.node.predecessor[0], self.node.successor[0]))
                print('[stabilize] {}: get_successors_predecessor() returned {} at {}'.format(self.node.id, x_id, x_ip))
            except:
                x_id = None

            if x_id is None:
                print('[stabilize] Sucessor has crashed!')
                continue

            if x_id != -1:
                n_x_distance = utils.circular_distance(self.node.id, x_id, self.node.ring_bits)
                n_succ_distance = utils.circular_distance(self.node.id, self.node.successor[0], self.node.ring_bits)

                # If x lies in (n, succ)
                if n_x_distance < n_succ_distance and n_x_distance != 0:
                    self.node.set_successor(x_id, x_ip)

            # successor.notify(self.id)
            self.node.notify_successor()
            self.node.check_predecessor()
            self.node.sync_successor_list()