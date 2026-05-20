import shutil

from helpers.api import API


def delete_all_us(cfg, taiga_session):
    iterate = True
    while iterate:
        resp = API(cfg, taiga_session).get_user_stories_list()
        data = resp.json()

        count = len(data)

        if count == 0:
            iterate = False
        else:
            for item in data:
                API(cfg, taiga_session).delete_us_by_id(item['id'])

def clear_allure_results_dir(dir_path):
    for item in dir_path.iterdir():
        if item.name != "history":
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
