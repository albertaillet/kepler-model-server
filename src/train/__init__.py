# comonly used within train module
from train.extractor.extractor import DefaultExtractor
from train.profiler.profiler import Profiler

DefaultProfiler = Profiler(extractor=DefaultExtractor())
