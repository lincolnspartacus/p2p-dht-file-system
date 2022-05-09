from threading import Thread
import random
import time
import utils

"""
* called periodically. refreshes finger table entries.
* next_finger stores the index of the next finger to fix.
"""

class FixFinger(Thread):

    def __init__(self, node):
        Thread.__init__(self)
        self.node = node
        self.ring_modulo = pow(2, self.node.ring_bits)

    def run(self):
        # Wait for for successor to get set properly
        while True:
            successor = self.node.get_successor()
            if successor[0] != -1 and successor[0] != self.node.id:
                break

        while True:
            low = 3
            high = 6
            sleep_time = random.randint(low, high)
            time.sleep(sleep_time)

            for next_finger in range(1, self.node.ring_bits): # Skip finger_table[0] because it is set elsewhere by Chord
                (id, ip) = self.node.ftable[next_finger]
                print('[fix_finger] {}: CurrentID {} CurrentNodeIP {}'.format(self.node.id, id, ip))
                id = self.node.id + pow(2, next_finger)
                id = id % self.ring_modulo

                # Successor will most likely be consistent because of stabilize thread. So route to it
                (suc_id, target_ip) = self.node.get_successor()
                #print('[fix_finger] {}: Target CurrentID {} CurrentNodeIP {}'.format(self.node.id, id, target_ip))
                (id, ip) = self.node.find_successor(id, target_ip)
                self.node.ftable[next_finger] = (id, ip)
                print('[fix_finger] {}: UpdatedID {} UpdatedNodeIP {}'.format(self.node.id, id, ip))
            
            print(self.node.ftable)
