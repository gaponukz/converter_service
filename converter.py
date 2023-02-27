from converter_script import converter_utils
import threading
import nest_asyncio
import asyncio
import patoolib
import shutil
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
                    path_to_save = f"results/{archive_id}/{client}_tdata"
                )),
            args=(client,)
        ))
    
    for threads in utils.devide_list(thread_groups, THREADS_LIMIT):
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]
    
    try:
        shutil.make_archive(f"results/{archive_id}", 'zip', f"results/{archive_id}")
    
    except Exception as error:
        print(f"{error.__class__.__name__}: {error}")
    
    try:
        shutil.rmtree(f"sessions/{archive_id}")
    
    except Exception as error:
        print(f"{error.__class__.__name__}: {error}")
    
    try:
        shutil.rmtree(f"results/{archive_id}")
    
    except Exception as error:
        print(f"{error.__class__.__name__}: {error}")

def from_tdata(archive_id: str):
    thread_groups = []

    def _convert(file: str):
        patoolib.extract_archive(f"tdatas/{archive_id}/{file}", 0, f"tdatas/{archive_id}")

        try:
            loop.run_until_complete(asyncio.wait_for(converter_utils.convert_from_tdata_to_session(
                f"tdatas/{archive_id}/{file}".replace('.zip', ''), f"results/{archive_id}"
            ), 10))
        
        except Exception as error:
            print(f"{error.__class__.__name__}: {error}")
        
        try:
            os.remove(f"tdatas/{archive_id}/{file}")
        
        except Exception as error:
            print(error)
        
    for file in os.listdir(f"tdatas/{archive_id}"):
        thread_groups.append(threading.Thread(
            target=_convert, args=(file,)
        ))
    
    os.mkdir(f"results/{archive_id}")

    for threads in utils.devide_list(thread_groups, THREADS_LIMIT):
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]

    try:
        shutil.rmtree(f"tdatas/{archive_id}")
    
    except Exception as error:
        print(f"{error.__class__.__name__}: {error}")

    try:
        shutil.make_archive(f"results/{archive_id}", 'zip', f"results/{archive_id}")

    except Exception as error:
        print(f"{error.__class__.__name__}: {error}")
    
    try:
        shutil.rmtree(f"results/{archive_id}")
    
    except Exception as error:
        print(f"{error.__class__.__name__}: {error}")
