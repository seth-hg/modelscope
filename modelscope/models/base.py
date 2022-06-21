# Copyright (c) Alibaba, Inc. and its affiliates.

import os.path as osp
from abc import ABC, abstractmethod
from typing import Dict, Union

from modelscope.hub.snapshot_download import snapshot_download
from modelscope.models.builder import build_model
from modelscope.utils.config import Config
from modelscope.utils.constant import ModelFile

Tensor = Union['torch.Tensor', 'tf.Tensor']


class Model(ABC):

    def __init__(self, model_dir, *args, **kwargs):
        self.model_dir = model_dir

    def __call__(self, input: Dict[str, Tensor]) -> Dict[str, Tensor]:
        return self.postprocess(self.forward(input))

    @abstractmethod
    def forward(self, input: Dict[str, Tensor]) -> Dict[str, Tensor]:
        pass

    def postprocess(self, input: Dict[str, Tensor],
                    **kwargs) -> Dict[str, Tensor]:
        """ Model specific postprocess and convert model output to
        standard model outputs.

        Args:
            inputs:  input data

        Return:
            dict of results:  a dict containing outputs of model, each
                output should have the standard output name.
        """
        return input

    @classmethod
    def from_pretrained(cls, model_name_or_path: str, *model_args, **kwargs):
        """ Instantiate a model from local directory or remote model repo
        """
        if osp.exists(model_name_or_path):
            local_model_dir = model_name_or_path
        else:
            local_model_dir = snapshot_download(model_name_or_path)
            # else:
            #     raise ValueError(
            #         'Remote model repo {model_name_or_path} does not exists')

        cfg = Config.from_file(
            osp.join(local_model_dir, ModelFile.CONFIGURATION))
        task_name = cfg.task
        model_cfg = cfg.model
        # TODO @wenmeng.zwm may should manually initialize model after model building
        if hasattr(model_cfg, 'model_type') and not hasattr(model_cfg, 'type'):
            model_cfg.type = model_cfg.model_type
        model_cfg.model_dir = local_model_dir
        for k, v in kwargs.items():
            model_cfg.k = v
        return build_model(model_cfg, task_name)