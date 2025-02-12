import click
from postomc import DepletionResults
import h5py
import pandas as pd
from pathlib import Path


@click.command()
@click.option("--file", "-f", type=str, help="Path to the depletion_results.h5 file.")
@click.option(
    "--split-nuclides",
    "-s",
    is_flag=True,
    default=False,
    show_default=True,
    help="Wether to create a nuclide indexed table or an (Element, A, I) indexed table.",
)
@click.option(
    "--unit",
    "-u",
    default="g/cm**3",
    type=str,
    help="The desired unit.",
    show_default=True,
)
@click.option(
    "--time-unit",
    "-t",
    default="d",
    type=str,
    help="The desired time unit.",
    show_default=True,
)
@click.option(
    "--output",
    "-o",
    default=None,
    type=str,
    help="Path to the output file.",
    show_default=True,
)
@click.option(
    "--chain",
    "-c",
    default=None,
    type=str,
    help="Path to a depletion chain file.",
    show_default=True,
)
@click.option(
    "--material",
    "-m",
    default=None,
    type=int,
    help="Id of the desired material",
    show_default=True,
)
def convert(file, split_nuclides, unit, time_unit, output, chain, material):
    if not h5py.is_hdf5(file):
        raise ValueError(f"{file} is not an HDF5 file")
    if "depletion time" not in h5py.File(file).keys():
        raise ValueError(f"{file} is not a depletion result file.")

    if output is None:
        to_console(file, split_nuclides, unit, time_unit, chain, material)
    elif output.split(".")[-1] == "csv":
        to_csv(file, split_nuclides, unit, time_unit, output, chain, material)
    elif output.split(".")[-1] == "xlsx":
        to_excel(file, split_nuclides, unit, time_unit, output, chain, material)
    else:
        to_console(file, split_nuclides, unit, time_unit, chain, material)


def to_console(file, split_nuclides, unit, time_unit, chain, material):
    res = DepletionResults(file, chain)
    materials = build_material_dict(file)

    dfs = res(unit, multiindex=split_nuclides, time_unit=time_unit, squeeze=False)
    if material is None and len(res.materials) == 1:
        material = dfs.keys()[0]
        click.echo(dfs[material].to_string())
    elif material is None and len(res.materials) != 1:
        for matid, df in dfs.items():
            click.echo(materials.get(matid, matid))
            click.echo(df.to_string())
            click.echo()
    else:
        if material not in dfs:
            raise ValueError(
                f"Material id {material} does not exist in file. Available: {list(dfs.keys())}"
            )
        else:
            click.echo(dfs[material].to_string())


def to_csv(file, split_nuclides, unit, time_unit, output, chain, material):
    res = DepletionResults(file, chain)
    # materials = build_material_dict(file)

    dfs = res(unit, multiindex=split_nuclides, time_unit=time_unit, squeeze=False)
    if material is None and len(res.materials) == 1:
        material = dfs.keys()[0]
        dfs[material].to_csv(output)
    elif material is None and len(res.materials) != 1:
        raise NotImplementedError(
            f"Can't convert multi-material result file to csv. Available materials {list(dfs.keys())}"
        )
    else:
        if material not in dfs:
            raise ValueError(
                f"Material id {material} does not exist in file. Available: {list(dfs.keys())}"
            )
        else:
            dfs[material].to_csv(output)


def to_excel(file, split_nuclides, unit, time_unit, output, chain, material):
    res = DepletionResults(file, chain)
    materials = build_material_dict(file)

    dfs = res(unit, multiindex=split_nuclides, time_unit=time_unit, squeeze=False)
    if material is None and len(res.materials) == 1:
        material = list(dfs.keys())[0]
        name = build_sheet_name(materials, material)
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            dfs[material].to_excel(writer, sheet_name=name)
    elif material is None and len(res.materials) != 1:
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            for matid, df in dfs.items():
                name = build_sheet_name(materials, matid)
                df.to_excel(writer, sheet_name=name)
    else:
        if material not in dfs:
            raise ValueError(
                f"Material id {material} does not exist in file. Available: {list(dfs.keys())}"
            )
        else:
            name = build_sheet_name(materials, material)
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                dfs[material].to_excel(writer, sheet_name=name)


def build_material_dict(file):
    summary = Path(file).parent / "summary.h5"
    if summary.exists():
        with h5py.File(summary) as f:
            materials = {}
            for material in f["materials"]:
                if f[f"materials/{material}"].attrs["depletable"] == 0:
                    continue
                id = int(material.split()[-1])
                name = f[f"materials/{material}/name"][()].decode("utf-8")
                materials[id] = name
        return materials
    else:
        return {}


def build_sheet_name(materials, material):
    name = materials.get(material, f"Material {material}")
    forbidden_mapping = {"/": "-", "\\": "-", "*": "x", "?": " ", "[": "(", "]": ")"}
    if len(name) > 31:
        return f"Material {material}"
    for k, v in forbidden_mapping.items():
        name = name.replace(k, v)
    return name
