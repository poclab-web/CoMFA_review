import glob
import json
import os
import time

import numpy as np
import pandas as pd

import calculate_conformation


def pkl_to_featurevalue(dir_name, dfp, mol, out_name):  # グリッド特徴量を計算　ボルツマン分布の加重はしないでデータセットの区別もなし。
    drop_dupl_x = dfp.drop_duplicates(subset="x").sort_values('x')["x"]
    drop_dupl_y = dfp.drop_duplicates(subset="y").sort_values('y')["y"]
    drop_dupl_z = dfp.drop_duplicates(subset="z").sort_values('z')["z"]

    d_x = (drop_dupl_x.iloc[1] - drop_dupl_x.iloc[0]) / 2
    d_y = (drop_dupl_y.iloc[1] - drop_dupl_y.iloc[0]) / 2
    d_z = (drop_dupl_z.iloc[1] - drop_dupl_z.iloc[0]) / 2
    for conf in mol.GetConformers():
        outfilename = "{}/{}/data{}.pkl".format(out_name, mol.GetProp("InchyKey"), conf.GetId())
        # if os.path.isfile(outfilename):
        #     continue
        filename = "{}/{}/data{}.pkl".format(dir_name, mol.GetProp("InchyKey"), conf.GetId())
        print(filename)
        data = pd.read_pickle(filename)
        # print(data)
        data["x"] = np.round((data["x"].values - min(drop_dupl_x)) / (d_x * 2)).astype(int)
        data["y"] = np.round((data["y"].values - min(drop_dupl_y)) / (d_y * 2)).astype(int)
        data["z"] = np.round((data["z"].values - min(drop_dupl_z)) / (d_z * 2)).astype(int)
        # data=data[min(drop_dupl_x)-d_x<data["x"]]
        data["Dt"] = data["Dt"].where(data["Dt"] < 10, 10)
        # #data[["x","y","z"]]=data[["x","y","z"]]
        # cond_x=[]
        # cond_y=[]
        # for x in drop_dupl_x:
        #     cond_x_=x-d_x<data["x"] and x+d_x>data["x"]
        #     cond_y_=
        start = time.time()
        Dt = []
        # for x in drop_dupl_x:
        #     data=data[x-d_x<data["x"]]
        #     data_x=data[x+d_x>data["x"]]
        #     for y in drop_dupl_y:
        #         data_x=data_x[y-d_y<data_x["y"]]
        #         data_y = data_x[y + d_y > data_x["y"]]
        #         for z in drop_dupl_z:
        #             data_y=data_y[z-d_z<data_y["z"]]
        #             data_z=data_y[z+d_z>data_y["z"]]
        #             Dt_=np.average(data_z["Dt"].values)
        #             Dt.append(Dt_)
        for x in range(len(drop_dupl_x)):
            data["x{}".format(x)] = data["x"] == x
        for y in range(len(drop_dupl_y)):
            data["y{}".format(y)] = data["y"] == y
        for z in range(len(drop_dupl_z)):
            data["z{}".format(z)] = data["z"] == z
        for x in range(len(drop_dupl_x)):
            # data_x=data[data["x"]==x]
            data_x = data[data["x{}".format(x)]]
            for y in range(len(drop_dupl_y)):
                # data_xy = data_x[data_x["y"] == y]
                data_xy = data_x[data_x["y{}".format(y)]]
                for z in range(len(drop_dupl_z)):
                    #Dt_ = np.sum(data_xy[data_xy["z{}".format(z)]]["Dt"].values)*(0.2*0.52917721067)**3
                    Dt_ = np.average(data_xy[data_xy["z{}".format(z)]]["Dt"].values)
                    Dt.append(Dt_)
        print(time.time() - start)
        # start=time.time()
        # for i,x in enumerate(dfp[["x","y","z"]].values):
        #     print("{}/{}".format(i,len(dfp)))
        #     data_=data[x[0]-d_x<data["x"]]
        #     data_=data_[x[0]+d_x>data_["x"]]
        #     dt=np.average(data_["Dt"].values)
        #     Dt.append(dt)
        #     if i==100:
        #         print(time.time()-start)
        #         sys.exit()
        dfp["Dt"] = np.nan_to_num(Dt)
        dfp.to_pickle(outfilename)

        # dfp_yz = dfp[(dfp["y"] > 0) & (dfp["z"] > 0)][["x", "y", "z"]].sort_values(['x', 'y', "z"],
        #                                                                            ascending=[True, True,
        #                                                                                       True])  # そとにでる
        # feature=["Dt"]
        # dfp_yz[feature] = \
        #                 dfp[(dfp["y"] > 0) & (dfp["z"] > 0)].sort_values(['x', 'y', "z"], ascending=[True, True, True])[
        #                     feature].values \
        #                 + dfp[(dfp["y"] < 0) & (dfp["z"] > 0)].sort_values(['x', 'y', "z"], ascending=[True, False, True])[
        #                     feature].values \
        #                 - dfp[(dfp["y"] > 0) & (dfp["z"] < 0)].sort_values(['x', 'y', "z"], ascending=[True, True, False])[
        #                     feature].values \
        #                 - dfp[(dfp["y"] < 0) & (dfp["z"] < 0)].sort_values(['x', 'y', "z"], ascending=[True, False, False])[
        #                     feature].values
        # # dfp_yz.to_csv(out_name + "/feature_yz_{}.csv".format(conf.GetId()))
        # print(dfp_yz)
        # filename = "{}/{}/data_yz{}.pkl".format(out_name, mol.GetProp("InchyKey"), conf.GetId())
        # dfp_yz.to_pickle(filename)


if __name__ == '__main__':
    dfs = []
    for path in glob.glob("../arranged_dataset/*.xlsx"):
        df = pd.read_excel(path)
        dfs.append(df)
    df = pd.concat(dfs).dropna(subset=['smiles']).drop_duplicates(subset=["smiles"])
    with open("../parameter/cube_to_grid/cube_to_grid0314.txt", "r") as f:
        param = json.loads(f.read())
    print(param)
    df["mol"] = df["smiles"].apply(calculate_conformation.get_mol)
    df = df[[os.path.isdir(param["cube_dir_name"] + "/" + mol.GetProp("InchyKey")) for mol in df["mol"]]]
    df["mol"].apply(
        lambda mol: calculate_conformation.read_xyz(mol, param["cube_dir_name"] + "/" + mol.GetProp("InchyKey")))
    dfp = pd.read_csv(param["grid_coordinates"] + "/coordinates.csv")
    print(dfp)
    for mol in df["mol"]:
        os.makedirs(param["grid_coordinates"] + "/" + mol.GetProp("InchyKey"), exist_ok=True)
        pkl_to_featurevalue(param["cube_dir_name"], dfp, mol, param["grid_coordinates"])
    # for file in glob.glob("../arranged_dataset/*.xlsx"):
    #     # for param_file_name in ["../parameter_0227/parameter_cbs_gaussian.txt",
    #     #                         "../parameter_0227/parameter_RuSS_gaussian.txt",
    #     #                         "../parameter_0227/parameter_dip-chloride_gaussian.txt", ][::-1]:
    #
    #     with open("../parameter/cube_to_grid/cube_to_grid.txt", "r") as f:
    #         param = json.loads(f.read())
    #     print(param)
    #     df = pd.read_excel(file).dropna(subset=['smiles'])[::-1]
    #     df["mol"] = df["smiles"].apply(calculate_conformation.get_mol)
    #     df = df[[os.path.isdir(param["cube_dir_name"] + "/" + mol.GetProp("InchyKey")) for mol in df["mol"]]]
    #     df["mol"].apply(
    #         lambda mol: calculate_conformation.read_xyz(mol, param["cube_dir_name"] + "/" + mol.GetProp("InchyKey")))
    #
    #     # if False:
    #     #     print(param["grid_sizefile"].split(","))
    #     #     l = param["grid_sizefile"].split(",")  # 4.5
    #     #     xgrid, ygrid, zgrid, gridinterval = [float(_) for _ in
    #     #                                          l]
    #     #     y_up = np.arange(gridinterval / 2, ygrid, gridinterval)
    #     #     y_down = -y_up
    #     #     y = np.sort(np.concatenate([y_down, y_up]))
    #     #     z_up = np.arange(gridinterval / 2, zgrid, gridinterval)
    #     #     z_down = -z_up
    #     #     print(z_up[-1])
    #     #     z = np.sort(np.concatenate([z_down, z_up]))
    #     #     sr = {"x": np.round(np.arange(-xgrid, 2.1, gridinterval), 3),
    #     #           # "y": np.round(np.arange(-ygrid, ygrid+0.1, gridinterval), 2),
    #     #           "y": np.round(y, 5),
    #     #           "z": np.round(z, 5)}
    #     #     dfp = pd.DataFrame([dict(zip(sr.keys(), l)) for l in product(*sr.values())]).astype(float).sort_values(
    #     #         by=["x", "y", "z"])
    #     # #else:
    #     #     dfp = pd.read_csv(
    #     #         "../grid_coordinates" + param["grid_coordinates_dir"] + "/[{}].csv".format(param["grid_sizefile"]))
    #     dfp = pd.read_csv(param["grid_coordinates"] + "/coordinates.csv")
    #     print(dfp)
    #
    #     # grid_dir_name = param["grid_dir_name"]
    #     # グリッド情報に変換
    #     for mol in df["mol"]:
    #         os.makedirs(param["grid_coordinates"]+"/" + mol.GetProp("InchyKey"),exist_ok=True)
    #         pkl_to_featurevalue(param["cube_dir_name"], dfp, mol,param["grid_coordinates"])
    #     #
    #     # file_name = os.path.splitext(os.path.basename(file))[0]
    #     # for mol, RT in df[["mol", "RT"]].values:
    #     #     print(mol.GetProp("InchyKey"))
    #     #     energy_to_Boltzmann_distribution(mol, RT)  # 温度が対応できていない#ボルツマン分布は最後のほうが良さそう
    #     #     read_cube(param["cube_dir_name"], dfp, mol, param["grid_coordinates"] + file_name + "/" + mol.GetProp(
    #     #         "InchyKey"))  # grid_dir_name + "/[{}]".format(param["grid_sizefile"]) +
    #     # print("complete")
