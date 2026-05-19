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
