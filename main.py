import requests
import json
import time
from dotenv import dotenv_values
import os
import logging

def initialize_logging(name=__name__, loglevel="ERROR", logfile_name="PLM.LOG"): 
    logger = logging.getLogger(name)
    if not isinstance(getattr(logging, loglevel.upper(), None), int):loglevel="ERROR"
    handler = logging.FileHandler(logfile_name)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(loglevel.upper())
    logger.info("Logging initialized")
    return logger

#migrate_bookmnarks()
def migrate_bookmnarks( linkding_base_url, 
                        linkding_api_key, 
                        json_filename='pinboard.json', 
                        logger=logging,
                        show_progressbar = True):
    start_time = time.time()
    json_file = open(json_filename)
    bookmarks_from_file = json.load(json_file)
    logger.debug("--- Loaded JSON in %s seconds ---" % (time.time() - start_time))

    start_time = time.time()
    url = f"{linkding_base_url}/api/bookmarks/"
    header = {'Authorization':f'Token {linkding_api_key}' }
    num_bookmarks = len(bookmarks_from_file)
    i = 0
    if show_progressbar: printProgressBar(0, num_bookmarks, prefix = 'Progress:', suffix = f'Complete({i}/{num_bookmarks})', length = 50)
    for bookmark in bookmarks_from_file:
        tags = bookmark['tags'].split(' ')
        #cleans up tags list if the source from pinboard is empty
        if " " in tags: tags.remove(" ")
        if "" in tags: tags.remove("")
        # adds "imported-from-pinboard" tag to better differentiate newly imported links
        tags.append("imported-from-pinboard")

        #API doesn't allow for specifying the date when the bookmark was saved. So save it as text in the description
        description_prefix = f"[Added from pinboard. Date in pinboard:{bookmark['time']}.]"
        data = {'url':bookmark['href'], 'title': bookmark['description'], 'description': f"{description_prefix}\n{bookmark['extended']}", 'notes':'', 'is_archived':'false', 'unread':bookmark['toread'],'shared':bookmark['shared']}
        if len(tags)>0: data['tag_names'] = tags
        response = requests.post(url, headers=header, data=data)
        if response.status_code == 201:logger.info( f"'{data['title']}' added.")
        else:logger.warn(f"Insert failed: Code:{response.status_code} Error:{response.text}" )
        i = i+1
        if show_progressbar: printProgressBar(i, num_bookmarks, prefix = 'Progress:', suffix = f'Complete({i}/{num_bookmarks})', length = 50)
    print("--- Finished importing in %s seconds ---" % "{:.2f}".format(time.time() - start_time))


def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    # Print iterations progress (from https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters)
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

env = dotenv_values()
logger = initialize_logging(loglevel=env['PLM_LOGLEVEL'],
                            logfile_name=env['PLM_LOG_FILENAME'])
migrate_bookmnarks(env['PLM_LINKDING_URL'],
                        env['PLM_LINKDING_API_KEY'],
                        json_filename=env['PLM_JSON_FILENAME'],
                        logger=logger,
                        show_progressbar=env['PLM_SHOW_PROGRESSBAR'])
    
    

