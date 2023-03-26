# fuente: https://github.com/techwithtim/Image-Scraper-And-Downloader/blob/main/tutorial.py

from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import io
from PIL import Image
import time

import os
import pandas as pd

PATH = "chromedriver.exe" # enter your local path

## valor = valor del billete (5, 10. 20...)
## max_images = número máximo de imágenes que se quieren obtener

def get_images(valor, max_images):
    
    # En esta url se buscan billetes de @valor euros en jpg y tamaño medium
	url = "https://www.google.com/search?q=billete%20de%20"+str(valor)+"%20euros&tbm=isch&hl=es&tbs=ift:jpg%2Cisz:m&sa=X&ved=0CAMQpwVqFwoTCKiv8q_J7f0CFQAAAAAdAAAAABAC&biw=1903&bih=961"
	wd = webdriver.Chrome(PATH)
	folder_path = 'dataset/images/'

	def get_images_from_google(wd, delay, max_images):
		def scroll_down(wd):
			wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			time.sleep(delay)

		wd.get(url)

		image_urls = set()
		skips = 0

		while len(image_urls) + skips < max_images:
			scroll_down(wd)

			thumbnails = wd.find_elements(By.CLASS_NAME, "Q4LuWd")

			for img in thumbnails[len(image_urls) + skips:max_images]:
				try:
					img.click()
					time.sleep(delay)
				except:
					continue

				images = wd.find_elements(By.CLASS_NAME, "n3VNCb")
				for image in images:
					if image.get_attribute('src') in image_urls:
						max_images += 1
						skips += 1
						break

					if image.get_attribute('src') and 'http' in image.get_attribute('src'):
						image_urls.add(image.get_attribute('src'))
						print(f"Found {len(image_urls)}")

		return image_urls


	def download_image(download_path, url, file_name):
		try:
			image_content = requests.get(url).content
			image_file = io.BytesIO(image_content)
			image = Image.open(image_file)
			file_path = download_path + file_name

			with open(file_path, "wb") as f:
				image.save(f, "JPEG")

			print("Success")
		except Exception as e:
			print('FAILED -', e)

	urls = get_images_from_google(wd, 1, max_images)

	for i, url in enumerate(urls):
		download_image(folder_path, url, str(valor)+'-'+str(i) + ".jpg")

	wd.quit()

# Save dataframe into csv with two columns: image path and value
def create_csv(path="dataset/images/"):
    dataset_source = path
    images = [[x, x.split('-')[0]] for x in os.listdir(dataset_source) if x[-3:] == "jpg"]
    df = pd.DataFrame(images, columns=['image', 'label'])
    df.to_csv('dataset/df.csv', index=False)