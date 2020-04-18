import pika


class Banker:
    def __init__(self, client_count, resources_count):
        self.client_count = client_count
        self.resources_count = resources_count
        self.preferred_cliend_id = 0
        self.available_resources = []
        self.max_demand = {}
        self.alloc_resources = {}
        self.need = {}

    def get_alloc_resources(self, config_file):
        with open(config_file, "r") as f:
            self.available_resources = [int(x) for x in f.readline().split(",")]
            for line in f:
                split_line = line.split(":")
                client_id = int(split_line[0])
                if client_id not in self.alloc_resources:
                    self.alloc_resources[client_id] = []
                split_line = split_line[1].split(",")
                for res in split_line:
                    self.alloc_resources[client_id].append(int(res))

    def calculate_need(self):
        for client in self.max_demand.keys():
            if client not in self.need:
                self.need[client] = []
            for num_res in range(len(self.max_demand[client])):
                self.need[client].append(
                    self.max_demand[client][num_res]
                    - self.alloc_resources[client][num_res]
                )

    def get_max_demand(self, chan):
        for client in range(1, self.client_count + 1):
            for _, _, body in chan.consume(queue=str(client), auto_ack=True):
                recv_buf = list(body)
                if recv_buf[0] > 100:
                    recv_buf[0] = recv_buf[0] % 100
                    self.preferred_cliend_id = recv_buf[0]
                if recv_buf[0] not in self.max_demand:
                    self.max_demand[recv_buf[0]] = []
                for res_num in range(self.resources_count):
                    self.max_demand[recv_buf[0]].append(recv_buf[res_num + 1])
                chan.cancel()
