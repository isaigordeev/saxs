from third_party.data_generation import Processing
from saxs.data_generation.generation import Generator
from saxs.data_generation import DEFAULT_CONFIG_PATH

import json


with open(DEFAULT_CONFIG_PATH) as config:
    generation_config = json.load(config)

if __name__ == '__main__':

    generator = Generator(**generation_config)

    # generator.generation()
    processing = Processing()


    # processing = Processing('/Users/isaigordeev/Desktop/generated/', 4000, 0)
    processing.process()