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
        self.next_finger = 0
        self.ring_modulo = pow(2, self.node.ring_bits)

    def run(self):

        time.sleep(30) # Wait for for successor to get set properly

        while True:
            low = 3
            high = 6
            sleep_time = random.randint(low, high)
            time.sleep(sleep_time)

            self.next_finger = (self.next_finger + 1) % self.node.ring_bits
            if self.next_finger == 0: # Skip finger_table[0] because it is set elsewhere by Chord
                continue
            (id, ip) = self.node.ftable[self.next_finger]
            print('[fix_finger] {}: CurrentID {} CurrentNodeIP {}'.format(self.node.id, id, ip))
            id = self.node.id + pow(2, self.next_finger) 
            id = id % self.ring_modulo
            
            # Successor will most likely be consistent because of stabilize thread. So route to it
            (suc_id, target_ip) = self.node.get_successor()
            #print('[fix_finger] {}: Target CurrentID {} CurrentNodeIP {}'.format(self.node.id, id, target_ip))
            (id, ip) = self.node.find_successor(id, target_ip)
            self.node.ftable[self.next_finger] = (id, ip)
            print('[fix_finger] {}: UpdatedID {} UpdatedNodeIP {}'.format(self.node.id, id, ip))
            print(self.node.ftable)
