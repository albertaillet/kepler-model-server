# TODO: test
import time


from train.prom.prom_query import PrometheusClient
from util.prom_types import get_valid_feature_group_from_queries, PROM_QUERY_INTERVAL
from util.config import getConfig
from util.loader import DEFAULT_PIPELINE

SAMPLING_INTERVAL = PROM_QUERY_INTERVAL
SAMPLING_INTERVAL = getConfig("SAMPLING_INTERVAL", SAMPLING_INTERVAL)
SAMPLING_INTERVAL = int(SAMPLING_INTERVAL)

from util.train_types import PowerSourceMap, FeatureGroups
from train.pipeline import NewPipeline
from train.extractor.extractor import DefaultExtractor
from train.isolator.isolator import MinIdleIsolator, ProfileBackgroundIsolator
from train.profiler.profiler import load_all_profiles


default_trainers = ["GradientBoostingRegressorTrainer"]
abs_trainer_names = default_trainers + []
dyn_trainer_names = default_trainers + []


def initial_pipelines():
    target_energy_sources = target_energy_sources.keys()
    valid_feature_groups = FeatureGroups.keys()
    profiles = load_all_profiles()
    profile_pipeline = NewPipeline(
        DEFAULT_PIPELINE,
        abs_trainer_names,
        dyn_trainer_names,
        extractor=DefaultExtractor(),
        isolator=ProfileBackgroundIsolator(profiles),
        target_energy_sources=target_energy_sources,
        valid_feature_groups=valid_feature_groups,
    )
    non_profile_pipeline = NewPipeline(
        DEFAULT_PIPELINE,
        abs_trainer_names,
        dyn_trainer_names,
        extractor=DefaultExtractor(),
        isolator=MinIdleIsolator(),
        target_energy_sources=target_energy_sources,
        valid_feature_groups=valid_feature_groups,
    )
    return profile_pipeline, non_profile_pipeline


if __name__ == "__main__":
    profile_pipeline, non_profile_pipeline = initial_pipelines()
    prom_client = PrometheusClient()
    while True:
        prom_client.query()
        query_results = prom_client.snapshot_query_result()
        valid_feature_groups = get_valid_feature_group_from_queries(query_results.keys())
        for energy_source, energy_components in PowerSourceMap.items():
            for feature_group in valid_feature_groups:
                success, _, _ = profile_pipeline.process(query_results, energy_components, energy_source, feature_group=feature_group)
                if not success:
                    # failed to process with profile, try non_profile pipeline
                    success, _, _ = non_profile_pipeline.process(query_results, energy_components, energy_source, feature_group=feature_group)
                    if success:
                        non_profile_pipeline.save_metadata()
                else:
                    profile_pipeline.save_metadata()
        time.sleep(SAMPLING_INTERVAL)
