from azureml.core import Workspace, Experiment, Environment
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.core.compute_target import ComputeTargetException
from azureml.pipeline.core import Pipeline, PipelineData
from azureml.pipeline.steps import PythonScriptStep
from azureml.core.runconfig import RunConfiguration
from azureml.core.conda_dependencies import CondaDependencies
import os

# Initialize workspace
ws = Workspace.from_config()

# Create compute target
compute_name = "gpu-cluster"
try:
    compute_target = ComputeTarget(workspace=ws, name=compute_name)
except ComputeTargetException:
    compute_config = AmlCompute.provisioning_configuration(
        vm_size="STANDARD_NC6",
        max_nodes=4
    )
    compute_target = ComputeTarget.create(ws, compute_name, compute_config)
    compute_target.wait_for_completion(show_output=True)

# Create environment
env = Environment("car-racing-env")
conda_dep = CondaDependencies()
conda_dep.add_conda_package("python=3.8")
conda_dep.add_conda_package("numpy")
conda_dep.add_conda_package("tensorflow-gpu")
conda_dep.add_conda_package("pygame")
conda_dep.add_pip_package("azureml-core")
conda_dep.add_pip_package("azureml-pipeline-core")
conda_dep.add_pip_package("azureml-pipeline-steps")

env.python.conda_dependencies = conda_dep

# Create run configuration
run_config = RunConfiguration()
run_config.environment = env

# Create pipeline steps
train_step = PythonScriptStep(
    script_name="train.py",
    compute_target=compute_target,
    runconfig=run_config,
    source_directory=".",
    allow_reuse=False
)

# Create and run pipeline
pipeline = Pipeline(workspace=ws, steps=[train_step])
pipeline_run = Experiment(ws, 'car-racing-training').submit(pipeline)
pipeline_run.wait_for_completion()

# Register the trained model
model = pipeline_run.register_model(
    model_name='car-racing-dqn',
    model_path='outputs/models/',
    description='DQN model for car racing game'
)

# Create deployment configuration
from azureml.core.webservice import AciWebservice
from azureml.core.model import InferenceConfig

inference_config = InferenceConfig(
    source_directory=".",
    entry_script="app.py",
    environment=env
)

deployment_config = AciWebservice.deploy_configuration(
    cpu_cores=1,
    memory_gb=1
)

# Deploy the model
service = Model.deploy(
    workspace=ws,
    name="car-racing-service",
    models=[model],
    inference_config=inference_config,
    deployment_config=deployment_config
)

service.wait_for_deployment(show_output=True) 