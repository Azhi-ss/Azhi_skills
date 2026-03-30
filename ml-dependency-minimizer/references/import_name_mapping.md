# Import Name → PyPI Package Name Mapping

When Python import names differ from PyPI package names, both static and dynamic analysis can produce confusing results. Use this reference when writing `requirements.txt`.

## Common Mappings

| Import Name | PyPI Package | Notes |
|-------------|-------------|-------|
| `PIL` | `Pillow` | Python Imaging Library |
| `cv2` | `opencv-python` | Also `opencv-contrib-python` for extras |
| `yaml` | `PyYAML` | |
| `sklearn` | `scikit-learn` | |
| `skimage` | `scikit-image` | |
| `attr` | `attrs` | Not to be confused with `attr` (deprecated) |
| `bs4` | `beautifulsoup4` | |
| `dateutil` | `python-dateutil` | |
| `git` | `GitPython` | |
| `google.protobuf` | `protobuf` | |
| `Bio` | `biopython` | |
| `Crypto` | `pycryptodome` | Not `pycrypto` (unmaintained) |
| `serial` | `pyserial` | |
| `usb` | `pyusb` | |
| `wx` | `wxPython` | |
| `gi` | `PyGObject` | GTK bindings |
| `socks` | `PySocks` | |
| `lxml` | `lxml` | Same name, but sometimes confusing |
| `magic` | `python-magic` | |
| `jose` | `python-jose` | |
| `dotenv` | `python-dotenv` | |
| `pymongo` | `pymongo` | Same name |
| `bson` | `pymongo` | Bundled with pymongo |
| `dns` | `dnspython` | |

## ML / Deep Learning Specific

| Import Name | PyPI Package | Notes |
|-------------|-------------|-------|
| `torch` | `torch` | Use `--index-url` for CPU/GPU variants |
| `torchvision` | `torchvision` | Must match torch version |
| `torchaudio` | `torchaudio` | Must match torch version |
| `tensorflow` | `tensorflow` | GPU included since TF 2.x |
| `tf` | `tensorflow` | Common alias in scripts |
| `keras` | `keras` | Standalone since Keras 3 |
| `transformers` | `transformers` | HuggingFace |
| `datasets` | `datasets` | HuggingFace datasets |
| `tokenizers` | `tokenizers` | HuggingFace fast tokenizers |
| `accelerate` | `accelerate` | HuggingFace training |
| `wandb` | `wandb` | Weights & Biases |
| `mlflow` | `mlflow` | |
| `tensorboard` | `tensorboard` | |
| `tensorboardX` | `tensorboardX` | PyTorch TensorBoard |

## Chemistry / Science Specific

| Import Name | PyPI Package | Notes |
|-------------|-------------|-------|
| `rdkit` | `rdkit` or `rdkit-pypi` | Use `rdkit-pypi` for pip install |
| `openbabel` | `openbabel` | Also needs system lib |
| `ase` | `ase` | Atomic Simulation Environment |
| `pymatgen` | `pymatgen` | Materials science |

## How to Check

When in doubt, use:
```bash
# Check where a package actually comes from
python -c "import <name>; print(<name>.__file__)"

# Check the installed package name
pip show <name> 2>/dev/null || pip show $(pip freeze | grep -i <name>)
```
