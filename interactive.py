import random
import json
import asyncio
import time

from datasets import load_dataset
from tqdm.asyncio import tqdm_asyncio

from predictors import *
from llm import *
from prompts import *
from tools import *

from evaluations import *

from collections import defaultdict
import pandas as pd

import matplotlib.pyplot as plt
import numpy as np

BIG_MODEL = "gpt-4.1"
MEDIUM_MODEL = "gpt-4.1-mini"
SMALL_MODEL = "gpt-4.1-nano"

dataset = load_dataset("gsm8k", "main")
training, validation = build_datasets(dataset, 1000, 0.7)
ds = {
    'training': training,
    'validation': validation,
}





