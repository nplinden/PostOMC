import click
import os
import h5py
import matplotlib.pyplot as plt
from postomc.depletion_results import ureg
from postomc.depletion_results import DepletionResults

a_series_landscape_inches = {
    "A0": (46.81, 33.11),
    "A1": (33.11, 23.39),
    "A2": (23.39, 16.54),
    "A3": (16.54, 11.69),
    "A4": (11.69, 8.27),
    "A5": (8.27, 5.83),
    "A6": (5.83, 4.13),
    "A7": (4.13, 2.91),
    "A8": (2.91, 2.05),
    "A9": (2.05, 1.46),
    "A10": (1.46, 1.02),
}


def get_figsize(figsize):
    if figsize in a_series_landscape_inches:
        return a_series_landscape_inches[figsize]
    else:
        width, height = figsize.split()
        return float(width), float(height)


dimensions = {
    "atom": [ureg("atom").dimensionality, ureg("atom/cm**3").dimensionality],
    "mass": [ureg("g").dimensionality, ureg("g/cm**3").dimensionality],
    "activity": [ureg("Bq").dimensionality, ureg("Bq/cm**3").dimensionality],
    "heat": [ureg("W").dimensionality, ureg("W/cm**3").dimensionality],
}

DIMENSIONS = {
    ureg("atom").dimensionality: "Atom Number",
    ureg("atom/cm**3").dimensionality: "Atom Density",
    ureg("g").dimensionality: "Mass",
    ureg("g/cm**3").dimensionality: "Mass Density",
    ureg("Bq").dimensionality: "Activity",
    ureg("Bq/cm**3").dimensionality: "Activity Density",
    ureg("W").dimensionality: "Power",
    ureg("W/cm**3").dimensionality: "Power Density",
}


@click.command()
@click.argument("file", type=str)
@click.option("--nuclides", "-n", type=str)
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
    "--material",
    "-m",
    default=None,
    type=int,
    help="Id of the desired material",
    show_default=True,
)
@click.option(
    "--output",
    "-o",
    default="depletion.png",
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
    "--title",
    default="Depletion Results",
    type=str,
    help="Title of the plot.",
    show_default=True,
)
@click.option(
    "--figsize",
    default="A5",
    type=str,
    help="Size of the figure in paper sizes (A0, A1... A7).",
    show_default=True,
)
@click.option("--logy", "yscale", flag_value="log", default="linear")
@click.option("--logx", "xscale", flag_value="log", default="linear")
def plot(
    file,
    nuclides,
    unit,
    time_unit,
    material,
    output,
    chain,
    yscale,
    xscale,
    title,
    figsize,
):
    if not h5py.is_hdf5(file):
        raise ValueError(f"{file} is not an HDF5 file")
    if h5py.File(file)["/"].attrs["filetype"] != b"depletion results":
        raise ValueError(f"{file} is not a depletion result file.")

    if chain is None:
        chain = os.environ.get("OPENMC_CHAIN_FILE")
    res = DepletionResults(file, chain_file=chain)
    nmat = len(res.materials)
    if material is None and nmat > 1:
        raise ValueError(
            f"Multiple materials found ({nmat}), please specify a material with --material."
        )
    elif material is None and nmat == 1:
        material = list(res.materials.keys())[0]
    else:
        assert (
            material in res.materials
        ), f"Material {material} not found in the depletion results."

    if nuclides is None:
        raise ValueError("No nuclides specified for plotting.")
    nuclides = nuclides.split()
    fig, ax = plt.subplots(figsize=get_figsize(figsize))
    for nuclide in nuclides:
        df = res(unit, time_unit=time_unit, squeeze=False)[material]
        if nuclide not in df.index:
            raise ValueError(f"Nuclide {nuclide} not found in the depletion results.")
        series = df.loc[nuclide]
        ax.plot(series.index, series.values, label=nuclide)
    ax.set_title(title)
    ax.set_xscale(xscale)
    ax.set_yscale(yscale)
    ax.legend()
    ax.grid()
    ax.set_xlabel(f"Time [{time_unit}]")
    ax.set_ylabel(f"{DIMENSIONS[ureg(unit).dimensionality]} [{unit}]")
    fig.tight_layout()
    plt.savefig(output)
