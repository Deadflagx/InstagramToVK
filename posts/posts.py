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


pks = []                #Instagram posts
alllist = ''			


def photo(image_url,caption):
	""" Photo Uploader """
	response = requests.get(image_url)
	img = Image.open(BytesIO(response.content))
	width, height = img.size 
	img2 = img.crop((0,0,width,height))
	b = io.BytesIO()
	img2.save(b,format='PNG')
	b.seek(0)
	photo_list = upload.photo_wall(photos=b,group_id=group_id,caption=caption)
	attachment = ','.join('photo{owner_id}_{id}'.format(**item) for item in photo_list)
	return attachment

def video(video_url,description,name):
	""" Video Uploader """
	response = requests.get(video_url)
	video_data = BytesIO(response.content)
	video_list = upload.video(name=name,video_file=video_data,group_id=group_id,description=description)
	video_id = "video"+str(video_list['owner_id'])+"_"+str(video_list['video_id'])
	return video_id


""" Get accounts list from VK topic """
boardtext = vk.board.getComments(group_id=group_id,topic_id=41050203,count=1)
boardtext = boardtext['items'][0]['text']
splboardtext = boardtext.splitlines()
splboardtext = splboardtext[-1].split(']', 1)[0].lstrip('[')


while True:
	try:
		api.getTotalSelfFollowings()
		get = api.LastJson
		get = get['users']
		time.sleep(10)
	except (Exception) as e:
		print(traceback.format_exc())
	for x in get:
		try:
			api.getUserFeed(x['pk'],minTimestamp=int(datetime.timestamp(datetime.now() - timedelta(minutes=80))))  #Get post certain user in specified time
			get = api.LastJson
			time.sleep(10)
			username = 'instagram.com/'+x['username']
			if username not in boardtext:
				splboardtext = int(splboardtext)+1
				boardtext = boardtext+'\n'+'['+str(splboardtext)+'] '+username
				try:
					""" Update new usernames to topic list """
					vk.board.editComment(group_id=group_id,topic_id=41050203,comment_id=2,message=boardtext)
					time.sleep(10)
				except:
					print('vk.board error ')
			if get['items'] != []:
				try:
					for y in range(len(get['items'])):
						""" Get attachments from instagram """
						getusername = get['items'][0]['user']['username']
						username = 'instagram.com/'+getusername				   
						caption = get['items'][y]['caption']                   #Get instagram post caption
						code = 'instagram.com/p/' + get['items'][y]['code']    #Get link on post
						if caption == None:
							text = ''
						else:
							text = get['items'][y]['caption']['text']
						if get['items'][y]['pk'] not in pks:
							if 'carousel_media' in get['items'][y]:
								for x in get['items'][y]['carousel_media']:
									media_type = x['media_type']
									if media_type == 1:
										link_photo = x['image_versions2']['candidates'][0]['url']
										alllist += photo(link_photo,'Photo was taken from Instagram : ' + username + '\n\n' + text)+','
									if media_type == 2:
										link_video = x['video_versions'][0]['url']
										alllist += video(link_video,'Video was taken from Instagram : ' + username + '\n\n' + text,'vk.com/shibasandakitas    ' + username)+','
							elif 'video_versions' in get['items'][y]:
								link_video = get['items'][y]['video_versions'][0]['url']
								alllist += video(link_video,'Video was taken from Instagram : ' + username + '\n\n' + text,'vk.com/shibasandakitas    ' + username)+','
							elif 'video_versions' not in get['items'][y]:
								link_photo = get['items'][y]['image_versions2']['candidates'][0]['url']
								alllist += photo(link_photo,'Photo was taken from Instagram : ' + username + '\n\n' + text)+','
							try:
								""" Make new post to VK """
								vk.wall.post(owner_id=-+group_id,from_group=True,attachment=alllist,message='Instagram : ' + username + '\nLink on post : ' + code)
								alllist = ''
								pks.append(get['items'][y]['pk'])
							except:
								print(traceback.format_exc())
				except (Exception) as e:
					print(traceback.format_exc())
		except (Exception) as e:
			print('global err')
	time.sleep(3900)



