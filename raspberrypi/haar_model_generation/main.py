from itertools import count
import requests
from bs4 import BeautifulSoup
import uuid
from time import time
from multiprocessing.pool import ThreadPool
import cv2
import os
import threading

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


shared_array = []

wait_lock = threading.Semaphore(0)
mutex = threading.Semaphore(1)


def threadFunc():
    print(f"Thread {name} starting")
    while 1:
        if len(shared_array) == 0:
            wait_lock.acquire()
        if running[0] == 0:
            break


NUMBER_OF_THREADS = 10

if __name__ == "__main__":
    # Setup
    os.makedirs(neg, exist_ok=True)
    imageLinks = []

    # getting all video links
    for link in archive_url:
        imageLinks += getImageLinks(link)
    print(len(imageLinks))

    # Saving all images (threaded)
    start = time()
    for link in imageLinks:
        downloadImageAndProcess(link)
    print(f"Time to download: {time() - start}")
