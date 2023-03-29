import threading
import asyncio
import patoolib
import logging
import shutil
import utils
import os

from converter_script import converter_utils

THREADS_LIMIT = 7
TIMEOUT_LIMIT = 69

logging.basicConfig(
    filename='converter.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S'
)

async def from_session_worker(archive_id: str, client: str):
    logging.info(f'Try to convert from session {archive_id}/{client}')

    await converter_utils.convert_from_string_to_tdata(
        await converter_utils.get_client_string_session(client, f"sessions/{archive_id}"),
        path_to_save = f"results/{archive_id}/{client}/tdata"
    )

    logging.info(f'Converted from session {archive_id}/{client}')

async def from_tdata_worker(archive_id: str, file: str):
    logging.info(f'Try to convert from tdata {archive_id}/{file}')
    
    patoolib.extract_archive(f"tdatas/{archive_id}/{file}", 0, f"tdatas/{archive_id}/{file}".replace('.zip', ''))

    await converter_utils.convert_from_tdata_to_session(
        f"tdatas/{archive_id}/{file}".replace('.zip', ''), f"results/{archive_id}"
    )

    try:
        os.remove(f"tdatas/{archive_id}/{file}")

    except Exception as error:
        print(error)
    
    logging.info(f'Converted from tdata {archive_id}/{file}')

def from_session_sync_bridge(archive_id: str, client: str):
    asyncio.run(asyncio.wait_for(from_session_worker(archive_id, client), TIMEOUT_LIMIT))

def from_tdata_sync_bridge(archive_id: str, file: str):
    asyncio.run(asyncio.wait_for(from_tdata_worker(archive_id, file), TIMEOUT_LIMIT))

def from_session(archive_id: str):
    thread_groups = []
    clients = list(set([
        file.replace('.json', '').replace('.session', '')
        for file in os.listdir(f"sessions/{archive_id}")
    ]))

    for client in clients:
        thread_groups.append(threading.Thread(target = from_session_sync_bridge, args=(archive_id, client)))

    for threads in utils.devide_list(thread_groups, THREADS_LIMIT):
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]

    try:
        for folder in os.listdir(f"results/{archive_id}"):
            try:
                shutil.make_archive(f"results/{archive_id}{folder}", 'zip', f"results/{archive_id}{folder}")
        
            except Exception as error:
                logging.exception(error)
            
        shutil.make_archive(f"results/{archive_id}", 'zip', f"results/{archive_id}")

    except Exception as error:
        logging.exception(error)

    try:
        shutil.rmtree(f"sessions/{archive_id}")

    except Exception as error:
        logging.exception(error)

def from_tdata(archive_id: str):
    thread_groups = []

    for file in os.listdir(f"tdatas/{archive_id}"):
        thread_groups.append(threading.Thread(
            target=from_tdata_sync_bridge, args=(archive_id, file)
        ))

    os.mkdir(f"results/{archive_id}")

    for threads in utils.devide_list(thread_groups, THREADS_LIMIT):
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]

    try:
        shutil.rmtree(f"tdatas/{archive_id}")

    except Exception as error:
        logging.exception(error)

    try:
        shutil.make_archive(f"results/{archive_id}", 'zip', f"results/{archive_id}")

    except Exception as error:
        logging.exception(error)

    try:
        shutil.rmtree(f"results/{archive_id}")

    except Exception as error:
        logging.exception(error)

