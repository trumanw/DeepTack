class BasePredictor:
    def __init__(self, name, checkpoint=None):
        self.name = name
        self.checkpoint = checkpoint

    def predict(self, input_smiles):
        pass