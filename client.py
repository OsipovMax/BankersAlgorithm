import pika


class Client:
    def __init__(self, id, resources_count, prefer):
        self.client_id = id
        self.resources_count = resources_count
        self.local_max_demand = []
        self.is_preferred = prefer

    def get_local_max_demand(self, config_file):
        with open(config_file, "r") as f:
            for line in f:
                split_line = line.split(",")
                for num_res in range(self.resources_count):
                    self.local_max_demand.append(int(split_line[num_res]))

    def send_local_max_demand(self, chan):
        sending_buf = []
        if self.is_preferred:
            # preferred cliend
            sending_buf.append(self.client_id + 100)
        else:
            sending_buf.append(self.client_id)
        sending_buf += self.local_max_demand
        self.send_message(bytes(sending_buf), chan)

    def send_message(self, text_message, chan):
        chan.queue_declare(queue=str(self.client_id))
        chan.basic_publish(
            exchange="", routing_key=str(self.client_id), body=text_message
        )
