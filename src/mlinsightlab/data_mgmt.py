# Helper functions to manage and interact with MLFlow models
from .MLILException import MLILException
from .endpoints import DATA_UPLOAD, DATA_DOWNLOAD, LIST_DATA, GET_VARIABLE, LIST_VARIABLES, SET_VARIABLE, DELETE_VARIABLE, GET_PREDICTIONS, LIST_PREDICTIONS_MODELS
from typing import Any
import pandas as pd
import requests
import base64
import json
import io


def _list_data(
    url: str,
    creds: dict,
    directory: str
):
    """
    NOT MEANT TO BE CALLED BY THE END USER

    Lists all data avaialble to a user.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds: dict
        Dictionary that must contain keys "username" and "key", and associated values.
    directory: str
        Name of the directory you wish to view the contents of.
    """

    url = f"{url}/{LIST_DATA}"

    json_data = {
        'directory': directory
    }

    with requests.Session() as sess:
        resp = sess.post(
            url,
            auth=(creds['username'], creds['key']),
            json=json_data
        )

    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp


def _upload_data(
    url: str,
    creds: dict,
    file_path: str,
    file_name: str,
    overwrite: bool = False
):
    """
    NOT MEANT TO BE CALLED BY THE END USER

    Uploads a file to the MLIL platform's data store.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds: dict
        Dictionary that must contain keys "username" and "key", and associated values.
    file_path: str
        Path to the file to be uploaded to MLIL.
    file_name: str
        The name to give your file in the MLIL datastore.
    overwrite: bool
        Whether or not to overwrite the file, if a file of the same name
        already exists.
    """

    url = f"{url}/{DATA_UPLOAD}"

    with open(file_path, 'rb') as f:
        file_bytes = f.read()

    json_data = {
        'filename': file_name,
        'file_bytes': base64.b64encode(file_bytes).decode('utf-8'),
        'overwrite': overwrite
    }

    with requests.Session() as sess:
        resp = sess.post(
            url,
            auth=(creds['username'], creds['key']),
            json=json_data
        )

    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp


def _download_data(
    url: str,
    creds: dict,
    file_name: str,
    output_file_name: str
):
    """
    NOT MEANT TO BE CALLED BY THE END USER

    Downloads a file from the MLIL platform's data store as a byte string.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds: dict
        Dictionary that must contain keys "username" and "key", and associated values.
    file_name: str
        The name of the file to download.
    output_file_name: str
        The output name of the file to write to
    """

    url = f"{url}/{DATA_DOWNLOAD}"

    # TODO: Rewrite all of the below logic. Can be simplified
    json_data = {
        'filename': file_name
    }

    with requests.Session() as sess:
        resp = sess.post(
            url,
            auth=(creds['username'], creds['key']),
            json=json_data
        )

    if not resp.ok:
        raise MLILException(str(resp.json()))

    decoded_content = base64.b64decode(resp.content.decode('utf-8'))
    with open(output_file_name, 'wb') as f:
        f.write(decoded_content)


def _get_variable(
    url: str,
    creds: dict,
    variable_name: str
):
    """
    NOT MEANT TO BE CALLED BY THE END USER

    Retrieve a variable from the MLIL variable store.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds: dict
        Dictionary that must contain keys "username" and "key", and associated values.
    variable_name: str
        The name of the variable to access.
    """

    url = f"{url}/{GET_VARIABLE}/{variable_name}"

    with requests.Session() as sess:
        resp = sess.get(
            url,
            auth=(creds['username'], creds['key'])
        )

    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp


def _list_variables(
    url: str,
    creds: dict
):
    """
    NOT MEANT TO BE CALLED BY THE END USER

    Lists all variables associated with a user.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds: dict
        Dictionary that must contain keys "username" and "key", and associated values.
    """

    url = f"{url}/{LIST_VARIABLES}"

    with requests.Session() as sess:
        resp = sess.get(
            url,
            auth=(creds['username'], creds['key'])
        )

    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp


def _set_variable(
    url: str,
    creds: dict,
    variable_name: str,
    value: Any,
    overwrite: bool = False
):
    """
    NOT MEANT TO BE CALLED BY THE END USER

    Creates a variable within the MLIL variable store.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds: dict
        Dictionary that must contain keys "username" and "key", and associated values.
    variable_name: str
        The name of the variable to set.
    overwrite: bool = False
        Whether to overwrite any variables that currently exist in MLIL and have the same name.
    value: Any
        Your variable. Can be of type string | integer | number | boolean | object | array<any>.
    """

    url = f"{url}/{SET_VARIABLE}"

    json_data = {
        'variable_name': variable_name,
        'value': value,
        'overwrite': overwrite
    }

    with requests.Session() as sess:
        resp = sess.post(
            url,
            auth=(creds['username'], creds['key']),
            json=json_data
        )

    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp


def _delete_variable(
    url: str,
    creds: dict,
    variable_name: str
):
    """
    NOT MEANT TO BE CALLED BY THE END USER

    Removes a variable from the MLIL variable store.
    Called within the MLILClient class.

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds: dict
        Dictionary that must contain keys "username" and "key", and associated values.
    variable_name: str
        The name of the variable to delete.
    """

    url = f"{url}/{DELETE_VARIABLE}/{variable_name}"

    with requests.Session() as sess:
        resp = sess.delete(
            url,
            auth=(creds['username'], creds['key'])
        )

    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp


def _get_predictions(
        url: str,
        creds: dict,
        model_name: str,
        model_flavor: str,
        model_version_or_alias: str | int
):
    """
    NOT MEANT TO BE CALLED BY THE END USER

    Gets predictions that a model has made

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform.
    creds: dict
        Dictionary that must contain keys "username" and "key", and associated values.
    model_name: str
        The name of the model to get predictions from
    model_flavor: str
        The flavor of the model to get predictions from
    model_version: str | int
        The version of the model to get predictions from
    """
    url = f'{url}/{GET_PREDICTIONS}/{model_name}/{model_flavor}/{model_version_or_alias}'

    with requests.Session() as sess:
        resp = sess.get(
            url,
            auth=(creds['username'], creds['key'])
        )

    if not resp.ok:
        raise MLILException(str(resp.json()))
    return resp


def _list_prediction_models(
        url: str,
        creds: dict
):
    """
    NOT MEANT TO BE CALLED BY THE END USER

    Lists models that have stored predictions

    Parameters
    ----------
    url: str
        String containing the URL of your deployment of the platform
    creds: dict
        Dictionary that must contain keys "username" and "key", and associated values.
    """
    url = f'{url}/{LIST_PREDICTIONS_MODELS}'

    with requests.Session() as sess:
        resp = sess.get(
            url,
            auth=(creds['username'], creds['key'])
        )

    if not resp.ok:
        raise MLILException(str(resp.json()))

    return resp
