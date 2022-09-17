from datetime import datetime

from ao3downloader import fileio, parse_text, parse_xml, strings
from ao3downloader.actions import shared
from ao3downloader.ao3 import Ao3
from ao3downloader.repo import Repository
from tqdm import tqdm


def action():
    with Repository() as repo:

        filetypes = shared.get_download_types()

        print(strings.PINBOARD_PROMPT_DATE)
        getdate = True if input() == strings.PROMPT_YES else False
        if getdate:
            date_format = 'mm/dd/yyyy'
            print(strings.PINBOARD_PROMPT_ENTER_DATE.format(date_format))
            inputdate = input()
            date = datetime.strptime(inputdate, '%m/%d/%Y')
        else:
            date = None

        print(strings.PINBOARD_PROMPT_INCLUDE_UNREAD)
        exclude_toread = False if input() == strings.PROMPT_YES else True

        print(strings.AO3_PROMPT_IMAGES)
        images = True if input() == strings.PROMPT_YES else False

        api_token = fileio.setting(
            strings.PINBOARD_PROMPT_API_TOKEN, 
            strings.SETTINGS_FILE_NAME, 
            strings.SETTING_API_TOKEN)

        shared.ao3_login(repo)
        
        print(strings.PINBOARD_INFO_GETTING_BOOKMARKS)

        url = parse_text.get_pinboard_url(api_token, date)
        bookmark_xml = repo.get_xml(url)
        bookmarks = parse_xml.get_bookmark_list(bookmark_xml, exclude_toread)

        print(strings.PINBOARD_INFO_NUM_RETURNED.format(len(bookmarks)))

        folder = strings.DOWNLOAD_FOLDER_NAME
        logfile = shared.get_logfile()

        logs = fileio.load_logfile(logfile)
        if logs:
            print(strings.INFO_EXCLUDING_WORKS)
            titles = parse_text.get_title_dict(logs)
            unsuccessful = parse_text.get_unsuccessful_downloads(logs)
            bookmarks = list(filter(lambda x: 
                not fileio.file_exists(x['href'], titles, filetypes, folder) 
                and x['href'] not in unsuccessful, 
                bookmarks))

        print(strings.AO3_INFO_DOWNLOADING)

        fileio.make_dir(folder)

        ao3 = Ao3(repo, filetypes, folder, logfile, None, True, images)

        for item in tqdm(bookmarks):
            ao3.download(item['href'])
