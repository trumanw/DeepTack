import deepchem as dc
from deepchem.models.torch_models.dmpnn import DMPNNModel

from .base import BasePredictor

class TgPredictor(BasePredictor):
    def __init__(self, name, checkpoint):
        self.name = name
        self.checkpoint = checkpoint
        
        model= DMPNNModel()
        model.restore(checkpoint=self.checkpoint)
        self.model = model

    def predict(self, input_smiles):
        smis = [input_smiles]
        featurizer = dc.feat.DMPNNFeaturizer()
        loader = dc.data.InMemoryLoader(
            tasks = [self.name],
            featurizer = featurizer)
        dataset = loader.create_dataset(smis)
        df = self.model.predict(dataset)

        return df.tolist()[0][0]