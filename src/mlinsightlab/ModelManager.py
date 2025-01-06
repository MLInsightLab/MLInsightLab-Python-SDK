import docker
import os

from .MLILException import MLILException

class ModelManager:

    def __init__(
        self,
        model_image = 'ghcr.io/mlinsighttechnologies/mlinsightlab-model-container:main',
        model_network = 'mlinsightlab_model_network',
        mlflow_tracking_uri = 'http://mlflow:2244',
        model_port = '8888'
    ):
        
        # Create docker container client
        self.docker_client = docker.from_env()
        
        # Store the image, network, and port on which the images will be stored
        self.model_image = model_image if model_image else os.environ['MODEL_CONTAINER_IMAGE']
        self.model_network = model_network if model_network else os.environ['MODEL_NETWORK']
        self.mlflow_tracking_uri = mlflow_tracking_uri if mlflow_tracking_uri else os.environ['MLFLOW_TRACKING_URI']
        self.container_port = model_port if model_port else os.environ['MODEL_PORT']

        # Store the containers
        self.models = []

    def deploy_model(
            self,
            model_uri,
            model_name,
            model_flavor,
            model_version_or_alias
    ):
        model_container = self.docker_client.containers.run(
            self.model_image,
            auto_remove = True,
            environment = {
                'MODEL_URI': model_uri,
                'MODEL_FLAVOR': model_flavor,
                'MLFLOW_TRACKING_URI': self.mlflow_tracking_uri
            },
            network = self.model_network,
            name = f'mlinsightlab__model__{model_name}__{model_flavor}__{model_version_or_alias}',
            detach = True
        )
        self.models.append(
            {
                'model_name' : model_name,
                'model_flavor' : model_flavor,
                'model_version_or_alias' : model_version_or_alias,
                'container_name' : model_container.name
            }
        )

    def remove_deployed_model(
            self,
            model_name,
            model_flavor,
            model_version_or_alias,
    ):
        
        container_name = None
        for model in self.models:
            if model['model_name'] == model_name and model['model_flavor'] == model_flavor and model['model_version_or_alias'] == model_version_or_alias:
                container_name = model['container_name']
                break
        
        if container_name is None:
            raise MLILException('Container for that model not found')
        
        try:
            container = self.docker_client.containers.get(container_name)
        except:
            raise MLILException('Container for that model not found')
        
        try:
            container.stop()
            self.models = [
                model for model in self.models if model['container_name'] != container_name
            ]
        except Exception as e:
            raise MLILException(f'Error trying to stop containerized model: {str(e)}')
        
        return True
        
    def remove_all_models(self):
        for model in self.models:
            container = self.docker_client.containers.get(model['container_name'])
            container.stop()
        self.models = []

        return True
        