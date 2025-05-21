import pandas as pd
from pathlib import Path
import streamlit as st
from streamlit_ketcher import st_ketcher
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

from config import APP_TITLE, APP_ICON
from models.prediction import FACTORY_METHOD, predict_properties

thumbnail_renderer = JsCode("""
    class ThumbnailRenderer {
        init(params) {
            this.eGui = document.createElement('img');
            this.eGui.setAttribute('src', `data:image/svg+xml;base64,` + params.value);
            this.eGui.setAttribute('width', '250');
            this.eGui.setAttribute('height', 'auto');
        }
        getGui() {
            console.log(this.eGui);
            return this.eGui;
        }
    }
""")

# page config
st.set_page_config(
    page_title=f"Properties Prediction | {APP_TITLE}",
    page_icon=APP_ICON,
    layout="wide"
)

# content
st.title("Properties Prediction")

st.divider()

## 01 Select a Pre-trained Model
st.subheader("01 Select a Pre-trained Model")
st.session_state.fixed_aggrid_cols = ["Input SMILES", "Canonical SMILES", "2D Image"]

#FIXME: checkbox with model selector for predicting multiple properties
#FIXME: implement the method with remote file storage uri
# get available models list from remote
models_available_remote = ["Tg_DMPNN_390.pt", "Tg_DMPNN_400.pt"]
selected_model = st.selectbox(
    "Select a model",
    options=models_available_remote
)
st.session_state.optional_aggrid_cols = ["Tg"]
st.session_state.optional_aggrid_predictors = [
    str(Path(__file__).absolute().parent.parent / Path(f'data/checkpoints/{selected_model}'))
]

st.session_state.aggrid_models = []
for pred_name, pred_ckpt in zip(st.session_state.optional_aggrid_cols, st.session_state.optional_aggrid_predictors):
    st.session_state.aggrid_models.append(FACTORY_METHOD[pred_name](pred_name, pred_ckpt))

if "all_pred_mols" not in st.session_state:
    st.session_state.all_pred_mols = pd.DataFrame(columns=st.session_state.fixed_aggrid_cols+st.session_state.optional_aggrid_cols)

st.divider()

## 02 Input a Tackifier Molecule
st.subheader("02 Input a Tackifier Molecule")

# tabs for different molecule input method
smiles_input_tab, sketcher_input_tab = st.tabs(["SMILES", "Sketcher"])
# tab 1. SMILES
with smiles_input_tab:
    st.caption("Input a molecule via SMILES")
    input_smiles = st.text_input("Input SMILES", value="C1=C(OC(=C1)C=O)CO")
    pred_btn = st.button("Predict")
    if pred_btn:
        returned_df = predict_properties(input_smiles, st.session_state.aggrid_models)
        st.session_state.all_pred_mols = pd.concat(
            [returned_df, st.session_state.all_pred_mols]).reset_index(drop=True)

# tab 2. Sketcher
with sketcher_input_tab:
    st.caption("Input a molcule via 2D Sketcher")
    input_smiles = st_ketcher(molecule_format="SMILES")
    if input_smiles != "":
        returned_df = predict_properties(input_smiles, st.session_state.aggrid_models)
        st.session_state.all_pred_mols = pd.concat(
            [returned_df, st.session_state.all_pred_mols]).reset_index(drop=True)

st.divider()

## 03 List Molecules
st.subheader("03 List Molecules")

# dataframe list all the molecules with predicted properties
# load and display molecules if `all_pred_mols` is successfully cached
if "all_pred_mols" in st.session_state:
    st.caption("Property Prediction Table")

    go = GridOptionsBuilder.from_dataframe(st.session_state.all_pred_mols)
    go.configure_default_column(
        editable = False,
        filterable = True,
        resizable = True,
        sortable = True
    )
    # column styling
    for col_name in st.session_state.fixed_aggrid_cols+st.session_state.optional_aggrid_cols:
        go.configure_column(
            col_name,
            editable=False,
            type=["numericColumn", "numberColumnFilter", "centerAligned"],
            cellStyle={"fontSize": "14px"},
        )

    go.configure_column(
        "2D Image", 
        cellRenderer=thumbnail_renderer,
        pinned=True,
        autoHeight=True,
        wrapText=True)

    # build AgGrid and show
    grid_options = go.build()
    AgGrid(
        st.session_state.all_pred_mols, 
        theme="streamlit",
        gridOptions=grid_options,
        fit_columns_on_grid_load=False,
        enable_enterprise_modules=True,
        allow_unsafe_jscode=True,
        reload_data=True,
        custom_css={
            ".ag-header-cell-label": {"font-size": "14px"}
        })

else:
    st.caption("At least input one molecule and predict.")

st.divider()