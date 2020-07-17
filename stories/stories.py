from InstagramAPI import InstagramAPI
import requests
from vk_api import VkUpload,vk_api
from PIL import Image
from io import BytesIO
import io
import traceback
from datetime import datetime,timedelta
import time

group_id = 				#VK Group ID
token = 'token' 		#VK Group ADM token
vk = vk_api.VkApi(token=token) 
vk._auth_token()
vk = vk.get_api()
upload = VkUpload(vk)

login = "login"         #Instagram account login
password  =  "pass"     #instagram account password

api = InstagramAPI(login,password)
api.login()  


storys_pks = []              #Instagram story posts
alllist = ''			


def photosrory(pstory):
	"""Photo story uploader """
	response = requests.get(pstory)
	img = Image.open(BytesIO(response.content))
	width, height = img.size 
	img2 = img.crop((0,0,width,height))
	b = io.BytesIO()
	img2.save(b,format='PNG')
	b.seek(0)
	upload.story(file=b,file_type='photo',group_id=group_id)

def videostory(pvideo):
	""" Video story uploader """
	response = requests.get(pvideo)
	video_data = BytesIO(response.content)
	upload.story(file=video_data,file_type='video',group_id=group_id)


while True:
	try:
		""" Get self followings accounts """
		api.getTotalSelfFollowings()
		get = api.LastJson
		get = get['users']
	except (Exception) as e:
		print(traceback.format_exc())
	for x in get:
		try:
			""" Get story """
			api.getStory(x['pk'])
			time.sleep(10)
			storyitems = api.LastJson
			if storyitems['items'] != []:
				for y in storyitems['items']:
					mdtype = y['media_type']
					if mdtype == 1 and y['pk'] not in storys_pks:
						story_link_photo = y['image_versions2']['candidates'][0]['url']
						photosrory(story_link_photo)
						storys_pks.append(y['pk'])
						time.sleep(10)
					elif mdtype == 2 and y['pk'] not in storys_pks:
						story_link_video = y['video_versions'][0]['url']
						videostory(story_link_video)
						storys_pks.append(y['pk'])
						time.sleep(10)
		except:
			print('getStory error \n' + traceback.format_exc())
	time.sleep(4500)
	


