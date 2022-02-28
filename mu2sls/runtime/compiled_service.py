
class CompiledService:
    def __init__(self, logger):
        logger.init_env()
        self.logger = logger

    def init_clients(self, clients={}):
        self.logger.init_clients(clients)

    def reinit_env(self, name, req_id):
        self.logger.reinit_env(name, req_id)