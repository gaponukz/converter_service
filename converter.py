from converter_script import converter_utils
import threading
import nest_asyncio
import asyncio
import utils
import os

loop = asyncio.get_event_loop()
nest_asyncio.apply()

THREADS_LIMIT = 5

def from_session(archive_id: str):
    thread_groups = []
    clients = list(set([
        file.replace('.json', '').replace('.session', '')
        for file in os.listdir(f"sessions/{archive_id}")
    ]))

    for client in clients:
        thread_groups.append(threading.Thread(
            target = lambda client:
                loop.run_until_complete(converter_utils.convert_from_string_to_tdata(
                    loop.run_until_complete(converter_utils.get_client_string_session(client, f"sessions/{archive_id}")),
                    path_to_save = f"results/{archive_id}/{client}tdata"
                )),
            args=(client,)
        ))
    
    for threads in utils.devide_list(thread_groups, THREADS_LIMIT):
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]
    
    # TODO: save if like archive with archives (name: any string, folder name: literal "tdata")

def from_tdata(archive_id: str):
    pass
