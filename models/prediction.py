import base64
import traceback

import pandas as pd
from rdkit import Chem
from rdkit.Chem import Draw

from .tg import TgPredictor

FACTORY_METHOD = {
    "Tg": TgPredictor
}

def predict_properties(input_smiles, predictors):
    try: 
        canon_smi = Chem.CanonSmiles(input_smiles) 

        # get base64 encoded molecule image data
        mol = Chem.MolFromSmiles(canon_smi)
        d2d = Draw.MolDraw2DSVG(300, 150)
        d2d.DrawMolecule(mol)
        d2d.FinishDrawing()
        text = d2d.GetDrawingText()
        imtext = base64.b64encode(bytes(text, 'utf-8')).decode('utf8')

        new_record = {
            'Input SMILES': input_smiles,
            'Canonical SMILES': canon_smi,
            '2D Image': imtext
        }

        for pred in predictors:
            new_record[pred.name] = pred.predict(input_smiles)

        new_record_df = pd.DataFrame(new_record, index =[0])
        return new_record_df
    except Exception as exc:
        traceback.print_exc()
        raise(exc)