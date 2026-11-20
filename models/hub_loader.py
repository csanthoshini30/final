"""Resolve model artifacts and load models across Keras serialization versions."""

import json
import os
import shutil
import tempfile
from pathlib import Path

import h5py
import tensorflow as tf
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
    """Raised when a required model artifact cannot be resolved or loaded."""


class _CompatibleDense(tf.keras.layers.Dense):
    """Ignore a newer, null quantization field when deserializing Dense layers."""

    @classmethod
    def from_config(cls, config):
        config = dict(config)
        config.pop("quantization_config", None)
        return super().from_config(config)


def load_compatible_keras_model(model_path: str | Path):
    """Load a Keras model, sanitizing newer null metadata in legacy HDF5 files."""
    model_path = Path(model_path)
    custom_objects = {
        "Dense": _CompatibleDense,
        "keras.layers>Dense": _CompatibleDense,
    }
    try:
        return tf.keras.models.load_model(
            str(model_path), compile=False, custom_objects=custom_objects
        )
    except (TypeError, ValueError) as original_error:
        if "quantization_config" not in str(original_error):
            raise

    # Keras 3.0.5 rejects quantization_config even when the value is null.
    # Sanitize a temporary copy so the cached/source model is never changed.
    try:
        with tempfile.TemporaryDirectory(prefix="apm-keras-") as temp_dir:
            compatible_path = Path(temp_dir) / model_path.name
            shutil.copyfile(model_path, compatible_path)
            with h5py.File(compatible_path, "r+") as model_file:
                raw_config = model_file.attrs.get("model_config")
                if raw_config is None:
                    raise ModelArtifactError(
                        f"No HDF5 model configuration was found in {model_path.name}."
                    )
                if isinstance(raw_config, bytes):
                    raw_config = raw_config.decode("utf-8")
                config = json.loads(raw_config)

                def remove_null_quantization_metadata(value):
                    if isinstance(value, dict):
                        if value.get("quantization_config", "not-null") is None:
                            value.pop("quantization_config")
                        for child in value.values():
                            remove_null_quantization_metadata(child)
                    elif isinstance(value, list):
                        for child in value:
                            remove_null_quantization_metadata(child)

                remove_null_quantization_metadata(config)
                del model_file.attrs["model_config"]
                model_file.attrs["model_config"] = json.dumps(config)

            return tf.keras.models.load_model(
                str(compatible_path), compile=False, custom_objects=custom_objects
            )
    except Exception as exc:
        raise ModelArtifactError(
            f"Could not load Keras model {model_path.name} after applying the compatibility fix: {exc}"
        ) from exc


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
