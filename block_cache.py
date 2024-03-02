class BlockCache:
    def __init__(self):
        self.checkpoints = {}  # Maps block numbers to cached states

    def save_checkpoint(self, block_number, state):
        """Saves a checkpoint of the system state at a given block number."""
        self.checkpoints[block_number] = state

    def get_nearest_checkpoint(self, block_number):
        """Finds the nearest checkpoint before the given block number."""
        if not self.checkpoints:
            return 0, None
        nearest = max([b for b in self.checkpoints if b <= block_number], default=None)
        return nearest, self.checkpoints.get(nearest)

