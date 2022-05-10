import requests
from bs4 import BeautifulSoup
import uuid
from time import time
import cv2
import os
import threading
import concurrent.futures


# Pour l'instant 878 images, faut enlever celles qui sont déjà prises par contre...
archive_url = [
    "https://sites.tufts.edu/babybirds/region/western-birds/?chick_type=altricial"
    # "https://sites.tufts.edu/babybirds/region/western-birds/page/2/?chick_type=altricial",
    # "https://sites.tufts.edu/babybirds/region/western-birds/page/3/?chick_type=altricial",
    # "https://sites.tufts.edu/babybirds/region/western-birds/page/4/?chick_type=altricial",
    # "https://sites.tufts.edu/babybirds/region/western-birds/page/5/?chick_type=altricial",
    # "https://sites.tufts.edu/babybirds/region/western-birds/page/6/?chick_type=altricial",
    # "https://sites.tufts.edu/babybirds/region/western-birds/page/7/?chick_type=altricial",
]

neg = "neg"
pos = "pos"
IMAGE_DIMENSIONS = (100, 100)  # TODO CHANGER ça


def getImageLinks(url):
    # create response object
    r = requests.get(url)
    # create beautiful-soup object
    soup = BeautifulSoup(r.content, "html5lib")
    # find all links on web-page
    links = soup.findAll("a")
    # filter the link sending with .jpg ou jpeg (pas de png)
    imageLinks = [
        link["href"]
        for link in links
        if link["href"].endswith("jpeg") or link["href"].endswith("jpg")
    ]

    return imageLinks


def downloadImageAndProcess(link):
    fileEnding = link.split(".")[-1]
    fileName = str(uuid.uuid1()) + "." + fileEnding
    # create response object
    r = requests.get(link, stream=True)
    # download started
    with open(os.path.join(neg, fileName), "wb") as f:
        for chunk in r:
            f.write(chunk)
    img = cv2.imread(os.path.join(neg, fileName), cv2.IMREAD_GRAYSCALE)
    resized_image = cv2.resize(img, (100, 100))
    cv2.imwrite(os.path.join(neg, fileName), resized_image)


running = [1]
shared_array = []

wait_lock = threading.Semaphore(0)
mutex = threading.Semaphore(1)
main_thread_lock = threading.Semaphore(0)


def threadFunc(name):
    print(f"Thread {name} starting")
    while 1:
        mutex.acquire()
        if len(shared_array) == 0:
            mutex.release()
            main_thread_lock.release()
            wait_lock.acquire()
        if running[0] == 0:
            break
        link = shared_array.pop()
        mutex.release()
        downloadImageAndProcess(link)


NUMBER_OF_THREADS = 5

if __name__ == "__main__":
    # Setup
    os.makedirs(neg, exist_ok=True)
    imageLinks = []

    # getting all video links
    for link in archive_url:
        imageLinks += getImageLinks(link)

    # Saving all images (threaded)
    shared_array += imageLinks
    start = time()
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=NUMBER_OF_THREADS
    ) as executor:
        executor.map(threadFunc, range(NUMBER_OF_THREADS))
        main_thread_lock.acquire()
        print(f"Time to download: {time() - start}")
        running[0] = 0
        for i in range(NUMBER_OF_THREADS):
            wait_lock.release()

    # Rest of the code...
