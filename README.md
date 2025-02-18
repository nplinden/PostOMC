A class for reading OpenMC `depletion_results.h5` files.

# Installation

PostOMC is available on PyPI:

```sh
pip install postomc
```

This installs the `postomc` python package as well as the `pomc` command line script.

# API Usage

PostMC revolves around the `DepletionResults` which can be instantiated from a `depletion_results.h5` file:

```python
from postomc import DepletionResults
res = DepletionResults("path/to/depletion_results.h5")
```

The get the isotopic composition over time simply call the `DepletionResults` like a function, and provide the desired unit as argument:

```python
res("g/cm**3")
```

If your result file contains only a single medium, this returns a Pandas dataframe with nuclide names as row index and timestamps as columns:

```text
          0.0           1.0           2.0           3.0
H1        0.0  8.546804e-11  1.710615e-10  2.561159e-10
H2        0.0  9.163202e-17  3.674525e-16  8.276545e-16
H3        0.0  7.819664e-26  6.288458e-25  2.128727e-24
H4        0.0  0.000000e+00  0.000000e+00  0.000000e+00
H5        0.0  0.000000e+00  0.000000e+00  0.000000e+00
...       ...           ...           ...           ...
Ds271_m1  0.0  0.000000e+00  0.000000e+00  0.000000e+00
Ds272     0.0  0.000000e+00  0.000000e+00  0.000000e+00
Ds273     0.0  0.000000e+00  0.000000e+00  0.000000e+00
Ds279_m1  0.0  0.000000e+00  0.000000e+00  0.000000e+00
Rg272     0.0  0.000000e+00  0.000000e+00  0.000000e+00

[3820 rows x 4 columns]
```

If your result file contains multiples media, it will return a dictionnary mapping medium id to results dataframes.
If you want to look at derived quantities like decay heat of activity, you'll need to provide an OpenMC decay chain to get decay constant and energy release values:

```python
from postomc import DepletionResults
res = DepletionResults("path/to/depletion_results.h5", chain="path/to/chain.xml")
res("W")
res("W/cm**3")
res("Bq")
res("Bq/cm**3")
```

You can also set the time unit to whatever you prefer:

```python
res("W", time_unit="s")
```

PostOMC uses [pint](https://pint.readthedocs.io/en/latest/index.html) for unit management so any unit from the default `pint` definition file is valid as long as it is homogeneous to mass, number of atoms, power, activity, or the volumic counterparts.

We also define the `atom` unit as an alias for the `count` unit so you can do:

```python
res("atom/beer_barrel", time_unit="fortnight")
```

Sometimes you may want to get information like total mass of a certain element, regardless of isotope.
You can facilitate this treatment by providing the `multiindex=True` argument to the call, this will result in dataframes using [multiindex](https://pandas.pydata.org/docs/user_guide/advanced.html).

```text
          0.0           1.0           2.0           3.0
Z  A   I
H  1   0  0.0  0.000000e+00  0.000000e+00  0.000000e+00
   2   0  0.0  0.000000e+00  0.000000e+00  0.000000e+00
   3   0  0.0  4.284350e-12  3.445411e-11  1.166318e-10
   4   0  0.0  0.000000e+00  0.000000e+00  0.000000e+00
   5   0  0.0  0.000000e+00  0.000000e+00  0.000000e+00
...       ...           ...           ...           ...
Ds 271 1  0.0  0.000000e+00  0.000000e+00  0.000000e+00
   272 0  0.0  0.000000e+00  0.000000e+00  0.000000e+00
   273 0  0.0  0.000000e+00  0.000000e+00  0.000000e+00
   279 1  0.0  0.000000e+00  0.000000e+00  0.000000e+00
Rg 272 0  0.0  0.000000e+00  0.000000e+00  0.000000e+00

[3820 rows x 4 columns]
```

In addition to isotopic composition, you can retrieve:

* Reaction rates in $\mathrm{reaction}/s$ with `DepletionResults.rr(time_unit="s")`
* $k_\mathrm{eff}$ using `DepletionResults.keffs(time_unit="s")`
* Reactivity using `DepletionResults.rhos(time_unit="s")`

Time units are always "day" by default.

# CLI Usage

Installing PostOMC also provides the `pomc` CLI command:

```text
Usage: pomc [OPTIONS]

Options:
  -f, --file TEXT         Path to the depletion_results.h5 file.
  -s, --split-nuclides    Wether to create a nuclide indexed table or an
                          (Element, A, I) indexed table.
  -u, --unit TEXT         The desired unit.  [default: g/cm**3]
  -t, --time-unit TEXT    The desired time unit.  [default: d]
  -o, --output TEXT       Path to the output file.
  -c, --chain TEXT        Path to a depletion chain file.
  -m, --material INTEGER  Id of the desired material
  --help                  Show this message and exit.
```

The CLI allows you to convert results files to CSV, Excel, on print their content in the console as a formatted dataframe.

For instance to creating an Excel file in with a tab for each medium:

```console
pomc -f path/to/depletion_results.h5 -o mass.xlsx -u "g/cm**3"
```