import argparse
from datetime import datetime

from manager import *
from saxs_processing.p_peak_classification import PDefaultPeakClassificator
from saxs_processing.phase_classificator import DefaultPhaseClassificator


def main():
    now = datetime.now()

    parser = argparse.ArgumentParser(description='Make')

    parser.add_argument('-d', '--dir', help='Specify files')

    args = parser.parse_args()

    dir = args.dir

    test = Custom_Manager(current_session=now,
                          peak_classificator=PDefaultPeakClassificator,
                          phase_classificator=DefaultPhaseClassificator,
                          peak_data_directory=dir,
                          phase_data_directory=ANALYSE_DIR_SESSIONS_RESULTS,
                          )
    test.directory_processing()


if __name__ == '__main__':
    main()