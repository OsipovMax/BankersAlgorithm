import pika
import threading
import copy
from banker import Banker
from client import Client


class Worker:
    def __init__(self, id, client_count, res_count):
        self.worker_thread_id = id
        self.client_count = client_count
        self.res_count = res_count
        self.distrib_plans = []
        self.preferred_plans = []
        self.worker_thread = threading.Thread(target=self.work_target, args=())
        self.get_connection()

    def get_connection(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="localhost")
        )
        self.channel = self.connection.channel()

    def close_connection(self):
        self.channel.close()
        self.connection.close()

    def work_target(self):
        if self.worker_thread_id == 0:
            banker = Banker(self.client_count, self.res_count)
            banker.get_alloc_resources("banker.txt")
            banker.get_max_demand(self.channel)
            banker.calculate_need()
            need_copy = copy.deepcopy(banker.need)
            avail_res_copy = copy.deepcopy(banker.available_resources)
            distribution_plan = []
            self.check_valid_state(need_copy, avail_res_copy, banker, distribution_plan)
            if len(self.distrib_plans):
                print("Secure plans", self.distrib_plans)
                self.get_preferred_plans(banker)
            else:
                print("No secure plans")
        else:
            if self.worker_thread_id == 1:
                client = Client(self.worker_thread_id, self.res_count, True)
            else:
                client = Client(self.worker_thread_id, self.res_count, False)
            client.get_local_max_demand("client" + str(self.worker_thread_id) + ".txt")
            client.send_local_max_demand(self.channel)

    def is_less(self, l_lst, r_lst):
        for ind in range(len(l_lst)):
            if l_lst[ind] <= r_lst[ind]:
                continue
            else:
                return False
        return True

    def get_preferred_plans(self, banker):
        help_map = {}
        for plan in self.distrib_plans:
            pos = plan.index(banker.preferred_cliend_id)
            if pos not in help_map:
                help_map[pos] = []
            help_map[pos].append(plan)
        keys = list(help_map.keys())
        keys.sort()
        for key in keys:
            if len(help_map[key]) == 0:
                continue
            else:
                print("Plans for preferred client", help_map[key])
                break

    def check_valid_state(self, need, avail, banker, plan) -> bool:
        for client in need.keys():
            if self.is_less(need[client], avail):
                plan.append(client)
                if len(plan) == banker.client_count:
                    self.distrib_plans.append(plan[:])
                need_copy = copy.deepcopy(need)
                del need_copy[client]
                avail_copy = copy.deepcopy(avail)
                avail_copy = [
                    x + y for x, y in zip(avail_copy, banker.alloc_resources[client])
                ]
                self.check_valid_state(need_copy, avail_copy, banker, plan)
                plan.remove(client)

    def start_work(self):
        self.worker_thread.start()

    def finish_work(self):
        self.worker_thread.join()
