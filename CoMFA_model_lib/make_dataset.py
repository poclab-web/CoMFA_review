import os
import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import PandasTools
from sklearn.model_selection import train_test_split

def common(from_file_path):
    df = pd.read_excel(from_file_path, engine="openpyxl").dropna(subset=["smiles"])
    df["mol"] = df["smiles"].apply(Chem.MolFromSmiles)
    df = df.dropna(subset=['er.', "mol", "smiles"])
    df["inchikey"] = df["mol"].apply(lambda mol: Chem.inchi.MolToInchiKey(Chem.AddHs(mol)))
    df["er."]=df["er."].apply(lambda x:np.clip(x,0.25,99.75))
    df = df[df["mol"].map(lambda mol: not mol.HasSubstructMatch(Chem.MolFromSmarts("[I]")))]
    df["RT"] = 1.99 * 10 ** -3 * df["temperature"].values
    df["ΔΔG.expt."] = df["RT"].values * np.log(100 / df["er."].values - 1)
    return df

def output(df,to_file_path):
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=4)
    train_df['test'] = 0
    test_df['test'] = 1
    df = pd.concat([train_df, test_df])

    PandasTools.AddMoleculeColumnToFrame(df, "smiles")
    df = df[["entry","smiles", "ROMol", "inchikey", "er.", "RT", "ΔΔG.expt.","Reference url","test"]].drop_duplicates(
        subset="inchikey")
    PandasTools.SaveXlsxFromFrame(df, to_file_path, size=(100, 100))

    df["aliphatic_aliphatic"]=df["ROMol"].map(lambda mol: mol.HasSubstructMatch(Chem.MolFromSmarts("CC(=O)C")))
    df["aliphatic_aromatic"]=df["ROMol"].map(lambda mol: mol.HasSubstructMatch(Chem.MolFromSmarts("CC(=O)c")))
    df["aromatic_aromatic"]=df["ROMol"].map(lambda mol: mol.HasSubstructMatch(Chem.MolFromSmarts("cC(=O)c")))
    df["ring"]=df["ROMol"].map(lambda mol: mol.HasSubstructMatch(Chem.MolFromSmarts("[#6][C;R](=O)[#6]")))
    print(f'aliphatic_aliphatic aliphatic_aromatic aromatic_aromatic ring')
    print(len(df[df["aliphatic_aliphatic"]&~df["ring"]&~df["test"]]),len(df[df["aliphatic_aliphatic"]&~df["ring"]&df["test"]]),
          len(df[df["aliphatic_aromatic"]&~df["ring"]&~df["test"]]),len(df[df["aliphatic_aromatic"]&~df["ring"]&df["test"]]),
          len(df[df["aromatic_aromatic"]&~df["ring"]&~df["test"]]),len(df[df["aromatic_aromatic"]&~df["ring"]&df["test"]]),
          len(df[df["ring"]&~df["test"]]),len(df[df["ring"]&df["test"]]))

if __name__ == '__main__':

    
    df_cbs=common("C:/Users/poclabws/PycharmProjects/CoMFA_model/sampledata/CBS.xlsx")
    df_dip=common("C:/Users/poclabws/PycharmProjects/CoMFA_model/sampledata/DIP.xlsx")
    df_ru=common("C:/Users/poclabws/PycharmProjects/CoMFA_model/sampledata/Ru.xlsx")
    
    to_dir_path = "C:/Users/poclabws/PycharmProjects/CoMFA_model/all_dataset"
    os.makedirs(to_dir_path, exist_ok=True)
    output(df_cbs,f'{to_dir_path}/CBS.xlsx')
    output(df_dip,f'{to_dir_path}/DIP.xlsx')
    output(df_ru,f'{to_dir_path}/Ru.xlsx')

    df_cbs = df_cbs[df_cbs["mol"].map(lambda mol: not mol.HasSubstructMatch(Chem.MolFromSmarts("n")))]
    df_dip=df = df_dip[df_dip["mol"].map(lambda mol:
                              not mol.HasSubstructMatch(Chem.MolFromSmarts("[#6]C(=O)[#6][#7,OH1]"))
                              and not mol.HasSubstructMatch(Chem.MolFromSmarts("[#6]C(=O)[#6]*[#7,OH1]"))
                              and not mol.HasSubstructMatch(Chem.MolFromSmarts("[#6]C(=O)[#6]**[#7,OH1]")))]
    
    to_dir_path = "C:/Users/poclabws/PycharmProjects/CoMFA_model/arranged_dataset"
    os.makedirs(to_dir_path, exist_ok=True)
    output(df_cbs,f'{to_dir_path}/CBS.xlsx')
    output(df_dip,f'{to_dir_path}/DIP.xlsx')
    output(df_ru,f'{to_dir_path}/Ru.xlsx')