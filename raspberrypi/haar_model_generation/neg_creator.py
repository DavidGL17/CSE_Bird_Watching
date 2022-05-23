import requests
from bs4 import BeautifulSoup
import uuid
from time import time
import cv2
import os
import threading
import re
import json
import concurrent.futures
from serpapi import GoogleSearch
import urllib.request


# Pour l'instant 878 images, faut enlever celles qui sont déjà prises par contre...
neg = "neg"
pos = "pos"
IMAGE_DIMENSIONS = (500, 500)  # TODO CHANGER ça


def getImageLinks(ijn):
    imageLinks = []
    params = {
        "api_key": "a1e0d2dc9bcf21d0930c041bc5c76704ba24f612ab04e002870829a56f7a6efe",
        "engine": "google",
        "q": "bird nest empty",
        "tbm": "isch",
        "ijn": ijn,
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    # print(json.dumps(results['suggested_searches'], indent=2, ensure_ascii=False))

    # -----------------------
    # Downloading images
    opener = urllib.request.build_opener()
    opener.addheaders = [
        (
            "User-Agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582",
        )
    ]
    urllib.request.install_opener(opener)

    for index, image in enumerate(results["images_results"]):
        try:
            print(f"image {index}...")
            fileName = str(uuid.uuid1()) + ".jpg"
            imageLinks.append(image["original"])
            urllib.request.urlretrieve(image["original"], os.path.join(neg, fileName))
            img = cv2.imread(os.path.join(neg, fileName), cv2.IMREAD_GRAYSCALE)
            resized_image = cv2.resize(img, IMAGE_DIMENSIONS)
            cv2.imwrite(os.path.join(neg, fileName), resized_image)
        except:
            continue

    return imageLinks


def downloadImageAndProcess(link):
    fileEnding = link.split(".")[-1]
    fileName = str(uuid.uuid1()) + "." + fileEnding
    opener = urllib.request.build_opener()
    opener.addheaders = [
        (
            "User-Agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582",
        )
    ]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(link, os.path.join(neg, fileName))
    img = cv2.imread(os.path.join(neg, fileName), cv2.IMREAD_GRAYSCALE)
    resized_image = cv2.resize(img, IMAGE_DIMENSIONS)
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
        print(len(shared_array))
        link = shared_array.pop()
        mutex.release()
        downloadImageAndProcess(link)


def createDescFile():
    for file_type in [neg]:
        for img in os.listdir(file_type):
            if file_type == neg:
                line = file_type + "/" + img + "\n"
                with open("bg.txt", "a") as f:
                    f.write(line)


def duplicateAndprocessImages():
    images = ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg"]
    for img_ref in images:
        print(f"doing image {img_ref}")
        ref_img = cv2.imread(os.path.join("ref", img_ref))
        resized_image = cv2.resize(ref_img, IMAGE_DIMENSIONS)
        img_name = img_ref.split(".")[0]
        file_ending = img_ref.split(".")[-1]
        for i in range(200):
            final_path = f"{img_name}-{i}.{file_ending}"
            cv2.imwrite(os.path.join("neg", final_path), resized_image)


NUMBER_OF_THREADS = 7

if __name__ == "__main__":

    # Saving all images (threaded)
    # shared_array += imageLinks
    # print(f"Preparing to download {len(shared_array)} images...")
    # start = time()
    # with concurrent.futures.ThreadPoolExecutor(
    #     max_workers=NUMBER_OF_THREADS
    # ) as executor:
    #     executor.map(threadFunc, range(NUMBER_OF_THREADS))
    #     main_thread_lock.acquire()
    #     print(f"Time to download: {time() - start}")
    #     running[0] = 0
    #     for i in range(NUMBER_OF_THREADS):
    #         wait_lock.release()

    # Setup
    os.makedirs(neg, exist_ok=True)
    # # getting all video links
    # # start = time()
    # # for ijn in range(6):
    # #     getImageLinks(str(ijn))
    # # print(f"Time to download: {time() - start}")
    # Creating negative images descritpion file
    duplicateAndprocessImages()
    createDescFile()
    # img = cv2.imread("bird5100100.jpg", cv2.IMREAD_ANYCOLOR)
    # resized_image = cv2.resize(img, (50, 50))
    # cv2.imwrite("bird5100100.jpg", resized_image)
