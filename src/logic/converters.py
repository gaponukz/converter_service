import os
import asyncio
import logging
import threading

from src import utils
from src.logic.interfaces import IConverter
from src.converter_script import converter_utils

THREADS_LIMIT = 7
TIMEOUT_LIMIT = 69

class FromTdataToSessionConverter(IConverter):
    def convert(self, input_folder: str, output_folder: str):
        thread_groups = []

        for file in os.listdir(input_folder):
            thread_groups.append(threading.Thread(
                target=self._from_tdata_sync_bridge, args=(input_folder, file)
            ))

        os.mkdir(output_folder)

        for threads in utils.devide_list(thread_groups, THREADS_LIMIT):
            [thread.start() for thread in threads]
            [thread.join() for thread in threads]

        utils.remove_folder(input_folder)
        utils.make_zip_archive(output_folder, output_folder)
        utils.remove_folder(output_folder)

    def _from_tdata_sync_bridge(self, input_folder: str, output_folder: str, file: str):
        asyncio.run(asyncio.wait_for(self._from_tdata_worker(input_folder, output_folder, file), TIMEOUT_LIMIT))

    async def _from_tdata_worker(self, input_folder: str, output_folder: str, file: str):
        logging.info(f'Try to convert from tdata {input_folder}/{file}')
        
        utils.unzip_archive(f"{input_folder}/{file}", f"{input_folder}/{file}".replace('.zip', ''))

        await converter_utils.convert_from_tdata_to_session(
            f"{input_folder}/{file}".replace('.zip', ''), output_folder
        )

        utils.remove_file(f"{input_folder}/{file}")
                
        logging.info(f'Converted from tdata {input_folder}/{file}')

class FromSessionToTdataConverter(IConverter):
    def convert(self, input_folder: str, output_folder: str):
        thread_groups = []
        clients = list(set([
            file.replace('.json', '').replace('.session', '')
            for file in os.listdir(input_folder)
        ]))

        for client in clients:
            thread_groups.append(threading.Thread(target = self._from_session_sync_bridge, args=(input_folder, output_folder, client)))

        for threads in utils.devide_list(thread_groups, THREADS_LIMIT):
            [thread.start() for thread in threads]
            [thread.join() for thread in threads]

        for folder in os.listdir(output_folder):
            utils.make_zip_archive(f"{output_folder}/{folder}", f"{output_folder}/{folder}")
        
        utils.make_zip_archive(output_folder, output_folder)
        utils.remove_folder(input_folder)

    def _from_session_sync_bridge(self, input_folder: str, output_folder: str, client: str):
        asyncio.run(asyncio.wait_for(self._from_session_worker(input_folder, output_folder, client), TIMEOUT_LIMIT))

    async def _from_session_worker(self, input_folder: str, output_folder: str, client: str):
        logging.info(f'Try to convert from session {input_folder}/{client}')

        await converter_utils.convert_from_string_to_tdata(
            await converter_utils.get_client_string_session(client, input_folder),
            path_to_save = f"{output_folder}/{client}/tdata"
        )

        logging.info(f'Converted from session {input_folder}/{client}')
