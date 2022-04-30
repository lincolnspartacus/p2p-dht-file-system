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
            try:
                succ_pred_id, succ_pred_ip = self.node.get_successors_predecessor()
                print('[stabilize] {}: get_successors_predecessor() returned {} at {}'.format(self.node.id, succ_pred_id, succ_pred_ip))
            except:
                succ_pred_id = None

            if succ_pred_id == None:
                #Successor doesn't exist/dead
                #delete current successor -> point to next available closest node
                self.node.delete_successor()
                # TODO: notify successor - leave 
                self.node.notify_successor(type='leave')
            elif succ_pred_id == -1: #self.node.successor[0]:
                # IN reference, there was self loop from successor to itself in predecessor link
                # successor does not have a predecessor yet, notify it
                # TODO: notify successor - join 
                self.node.notify_successor(type='join')
            else:
                # Update self successor as predecessor of current succesor
                # predeccesor of (predecessor of current succesor) will be updated in next iteration
                if succ_pred_id == self.node.id:
                    self.node.update_kth_finger_table_entry(0, succ_pred_id, succ_pred_ip)
                    print('[stabilize] {}: successor has been changed to {}'.format(self.node.id, self.node.successor))
                else: 
                    print('[stabilize] {}: skipping finger table update {}'.format(self.node.id, self.node.successor))
