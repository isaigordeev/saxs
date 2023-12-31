import argparse

from saxs.gaussian_processing.manager import *
from saxs.gaussian_processing.peak.p_peak_classification import PDefaultPeakClassificator
from saxs.gaussian_processing.phase.phase_classificator import AbstractPhaseKernel




def main():
    now = datetime.now()

    parser = argparse.ArgumentParser(description='Make')

    parser.add_argument('-d', '--dir', help='Specify files')

    args = parser.parse_args()

    dir = args.dir

    test = Custom_Manager(current_session=now,
                          peak_classificator=PDefaultPeakClassificator,
                          phase_classificator=AbstractPhaseKernel,
                          peak_data_directory=dir,
                          phase_data_directory=ANALYSE_DIR_SESSIONS_RESULTS,
                          )
    test.directory_processing()


if __name__ == '__main__':
    main()