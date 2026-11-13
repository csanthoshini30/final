# Aircraft Predictive Maintenance System

A Streamlit dashboard for exploring aircraft engine, electrical, and hydraulic maintenance data. The repository includes trained model artifacts and sample datasets.

## Run Locally

Requires Python 3.12.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run dashboard/app.py
```

## Deploy to Streamlit Community Cloud

1. Push this project directory to the `main` branch of GitHub.
2. Create an app in Streamlit Community Cloud using that repository.
3. Set the main file to `dashboard/app.py` and use Python 3.12.
4. Deploy and review the build and runtime logs.

The engine, electrical, and hydraulic model artifacts are loaded on demand from the private Hugging Face model repository. In Streamlit Community Cloud, add a read token with access to that repository under **App settings > Secrets**:

```toml
HF_TOKEN = "<your-read-token>"
```

Model binaries and local model caches are excluded from Git; do not force-add them. The application downloads model files from Hugging Face as needed. Keep the sample datasets, background image, and maintenance manual in the repository. The app loads TensorFlow and trained models, so verify that the selected Cloud resource tier has enough memory; a successful local startup does not guarantee the free Cloud tier can host all models.

Keep `data/`, the background image, and maintenance manual in the repository. Keep model-loading source such as `models/hub_loader.py`, but leave model binaries in the private Hugging Face repository. Do not commit local virtual environments, secrets, or generated Python cache files.

## Project Layout

- `dashboard/app.py`: Streamlit entry point.
- `dashboard/`: Dashboard implementation.
- `agents/`: Engine, electrical, hydraulic, coordinator, and maintenance knowledge agents.
- `config/`: Project-relative data and model paths.
- `data/`: Included sample datasets and manuals.
- `models/`: Trained subsystem models.
- `preprocessing/`, `inference/`, and `training/`: Data and model workflows.