"""Resolve local model artifacts or download them from the private Hub repo."""

import os
from pathlib import Path

from huggingface_hub import hf_hub_download
from huggingface_hub.errors import (
    EntryNotFoundError,
    GatedRepoError,
    HfHubHTTPError,
    LocalTokenNotFoundError,
    RepositoryNotFoundError,
)

MODEL_REPO_ID = "Santhoshini30/aircraft-predictive-maintenance-models"


class ModelArtifactError(RuntimeError):
    """Raised when a required model artifact cannot be resolved."""


def _get_hf_token():
    token = os.environ.get("HF_TOKEN")
    if token and token.strip():
        return token.strip()

    try:
        import streamlit as st

        token = st.secrets.get("HF_TOKEN")
        if token and str(token).strip():
            return str(token).strip()
    except Exception:
        pass

    # Uses `hf auth login` credentials for local development.
    return True


def download_model_artifact(repo_path: str) -> Path:
    """Download one exact path from the model repo into the Hub cache."""
    normalized = repo_path.replace("\\", "/").strip("/")
    parts = Path(normalized).parts
    if not normalized or Path(normalized).is_absolute() or ".." in parts:
        raise ValueError("Model repository paths must be relative and cannot traverse directories.")
    filename = normalized if normalized.startswith("models/") else f"models/{normalized}"

    try:
        return Path(hf_hub_download(
            repo_id=MODEL_REPO_ID,
            filename=filename,
            repo_type="model",
            token=_get_hf_token(),
        ))
    except EntryNotFoundError as exc:
        raise ModelArtifactError(f"Required model artifact is missing from the Hub: {filename}") from exc
    except (RepositoryNotFoundError, GatedRepoError, LocalTokenNotFoundError) as exc:
        raise ModelArtifactError(
            "Cannot access the private Hugging Face model repository. Set HF_TOKEN in the environment "
            "or Streamlit Secrets, or run `hf auth login` for local development."
        ) from exc
    except HfHubHTTPError as exc:
        status = getattr(getattr(exc, "response", None), "status_code", None)
        if status in (401, 403):
            raise ModelArtifactError(
                "Hugging Face denied access. Check that HF_TOKEN is valid and has read access "
                "to the private model repository."
            ) from exc
        raise ModelArtifactError(
            f"Hugging Face could not download {filename} (HTTP {status or 'error'})."
        ) from exc
    except Exception as exc:
        raise ModelArtifactError(
            f"Failed to download {filename} ({type(exc).__name__}). Check network access and Hugging Face authentication."
        ) from exc


def resolve_model_path(model_directory: Path, filename: str) -> Path:
    """Prefer the original local artifact; otherwise fetch its matching Hub path."""
    if Path(filename).name != filename:
        raise ValueError("Model filename must not include a directory path.")

    local_path = Path(model_directory) / filename
    if local_path.is_file() and local_path.stat().st_size > 0:
        return local_path

    system_directory = Path(model_directory).name
    if system_directory not in {"engine", "electrical", "hydraulic"}:
        raise ValueError(f"Unsupported model directory: {system_directory}")
    return download_model_artifact(f"models/{system_directory}/{filename}")