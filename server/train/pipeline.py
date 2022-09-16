import os
import sys
import shutil

server_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(server_path)

from abc import ABCMeta, abstractmethod
from train_types import FeatureGroup, get_feature_group, ModelOutputType, is_weight_output
import json

from util.config import getConfig, getPath
from util.loader import get_save_path, get_archived_file

METADATA_FILENAME = 'metadata.json'

model_path =  getPath(getConfig('MODEL_PATH', 'models'))

for ot in ModelOutputType:
    ot_group_path = os.path.join(model_path, ot.name)
    if not os.path.exists(ot_group_path):
        os.mkdir(ot_group_path)
    for g in FeatureGroup:
        group_path = os.path.join(ot_group_path, g.name)
        if not os.path.exists(group_path):
            os.mkdir(group_path)

def get_model_group_path(output_type, feature_group):
    return os.path.join(model_path, output_type.name, feature_group.name)

class TrainPipeline(metaclass=ABCMeta):
    def __init__(self, model_name, model_class, model_file, features, output_type):
        self.model_name = model_name
        self.model_class = model_class
        self.model_file = model_file
        self.features = features
        self.output_type = output_type
        self.feature_group = get_feature_group(features)
        self.weight_type = is_weight_output(self.output_type)
        self.group_path = get_model_group_path(self.output_type, self.feature_group)
        print(self.group_path)
        self.save_path = get_save_path(self.group_path, self.model_name) 
        if not os.path.exists(self.save_path):
            os.mkdir(self.save_path)

    # call this only model is updated
    def update_metadata(self, item):
        print('update metadata')
        item['model_name'] = self.model_name
        item['model_class'] = self.model_class
        item['model_file'] = self.model_file
        item['features']= self.features
        item['fe_files'] = [] if not hasattr(self, 'fe_files') else self.fe_files
        item['output_type'] = self.output_type.name
        self.metadata = item
        metadata_file = os.path.join(self.save_path, METADATA_FILENAME)
        with open(metadata_file, "w") as f:
            json.dump(item, f)
        if not self.weight_type:
            self.archive_model()
            
    @abstractmethod
    def train(self, prom_client):
        return NotImplemented

    def archive_model(self):
        archived_file = get_archived_file(self.group_path, self.model_name) 
        print("achive model ", archived_file, self.save_path)
        shutil.make_archive(self.save_path, 'zip', self.save_path)

