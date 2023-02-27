from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect

import os
import sys
import shutil
import pathlib
import zipfile
import traceback
import patoolib
import random
import asyncio
import nest_asyncio

loop = asyncio.get_event_loop()
nest_asyncio.apply()

sys.path.insert(0, os.path.abspath('..'))

import utils
import file_system_utils
from . import converter_utils

converter_blueprint = Blueprint('converter_blueprint', __name__, template_folder='templates', static_folder='static')

@converter_blueprint.route("/converter", methods=['GET', 'POST'])
def converter_page():
    if request.method == "POST":
        if os.path.exists("converter_factory"):
            try: shutil.rmtree("converter_factory")
            except: pass
        
        os.mkdir("converter_factory")

        def convert_from_session_action(session_file):
            try:
                if session_file.endswith(".session"):
                    string_session = loop.run_until_complete(
                        converter_utils.get_client_string_session(
                            session_file.replace(".session", "").replace("converter_factory/", ''),
                            "converter_factory"
                        )
                    )

                    loop.run_until_complete(
                        converter_utils.convert_from_string_to_tdata(
                            string_session,
                            str(pathlib.Path.home() / "Downloads") + "\\tdata" + str(random.randint(0, 10**6))
                        )
                    )

            except Exception as error:
                print(f"Filed to convert {session_file} ({error.__class__.__name__}): {error} on line {error.__traceback__.tb_lineno}")
        
        def convert_from_tdata_action(tdatas_folder):
            accounts = []
            os.mkdir("converter_factory/result")
            for tdata_folder in tdatas_folder:
                try:
                    accounts.append(loop.run_until_complete(asyncio.wait_for(converter_utils.convert_from_tdata_to_session(f"converter_factory\\tdatas\\{tdata_folder}"), 10)))
                
                except Exception as error:
                    traceback.print_exc()
                    print(f"Filed to convert {tdata_folder} ({error.__class__.__name__}): {error} on line {error.__traceback__.tb_lineno}")
            
            zipfolder = zipfile.ZipFile(str(pathlib.Path.home() / "Downloads") + "\\converted_session" + str(random.randint(0, 10**6)) + ".zip", 'w', compression = zipfile.ZIP_STORED)

            for account in accounts:
                if account:
                    zipfolder.write(f"converter_factory/result/{account}.json")
                    zipfolder.write(f"converter_factory/result/{account}.session")
            
            zipfolder.close()
                
        if request.form.get('selected_convert_from') == "SESSION":
            for file in request.files.getlist('files'):
                if any([file.filename.endswith(ext) for ext in ['.zip', '.rar', '.tgz']]):
                    try:
                        file.save(f"converter_factory/{file.filename}")
                        folder_name = patoolib.extract_archive(f"converter_factory/{file.filename}", 0, "converter_factory/sessions")
                        
                        file_system_utils.move_to_root_folder("converter_factory", folder_name)
                        try: shutil.rmtree("converter_factory/sessions")
                        except: pass

                    except Exception as error:
                        print(f"Filed to save file {file.filename} ({error.__class__.__name__}): {error} on line {error.__traceback__.tb_lineno}")
                        return redirect('/converter')

                    for session_file in os.listdir("converter_factory"):
                        utils.StoppableThread(target=convert_from_session_action, args=(session_file,), name="converter").start()
                
                elif file.filename.endswith('.session'):
                    for _file in request.files.getlist('files'):
                        if _file.filename.endswith('.json') and _file.filename.split('.')[0] == file.filename.split('.')[0]:
                            _file.save(f"converter_factory/{_file.filename}")

                    file.save(f"converter_factory/{file.filename}")
                    convert_from_session_action(f"converter_factory/{file.filename}")
        
        elif request.form.get('selected_convert_from') == "TDATA":
            for file in request.files.getlist('files'):
                if any([file.filename.endswith(ext) for ext in ['.zip', '.rar', '.tgz']]):
                    try:
                        file.save(f"converter_factory/{file.filename}")
                        folder_name = patoolib.extract_archive(f"converter_factory/{file.filename}", 0, "converter_factory/tdatas")

                    except Exception as error:
                        print(f"Filed to save file {file.filename} ({error.__class__.__name__}): {error} on line {error.__traceback__.tb_lineno}")
                        return redirect('/converter')
                    
            utils.StoppableThread(target=convert_from_tdata_action, args=(os.listdir("converter_factory/tdatas"),), name="converter").start()
        
            return redirect('/converter')
    
    text = file_system_utils.get_pages_text('wrapper_interface', 'converter', 'accounts_table')

    return render_template(
        'converter.html',
        title = text["converter"],
        accounts = [],
        accounts_status = {},
        working_without_proxy = True,
        text = text
    )
