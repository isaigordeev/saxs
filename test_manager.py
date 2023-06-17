from manager import *
manager = Manager(current_session)
# manager.atomic_processing('075775_treated_xye')
# manager.custom_repo_processing()

manager.repo_processing()
manager.write_data()


time_finish = time.time()
print(time_finish-time_start1)
print(time_finish-time_start2)