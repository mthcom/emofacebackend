from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

from django.http import JsonResponse

from distutils.dir_util import copy_tree
from shutil import copyfile

import os
import base64

from emoface.emotion import Emotion

detector = Emotion()

def index(request): #return all the names
    names = os.listdir('emoface/database')
    if request.method == 'POST':
        avatar_name = request.POST['name'].lower()

        success = False
        for n in names:
            if avatar_name == n.lower():
                success = True
                break
        if success:
            with open(os.path.join("emoface", "database", ".default"), "w") as default_file:
                default_file.write(avatar_name)
            return HttpResponse("success")
        else:
            return HttpResponse("avatar name not found")
    else:
        response = []

        for n in names:
            if n[0] == '.':
                continue
            with open(os.path.join("emoface", "database", n, "thumb.jpg"), "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            response.append({"name":n, "thumb":encoded_string})

        return JsonResponse(response, safe=False)

def add_image(request, name, emotion):
    if request.method == 'POST':
        new_image = request.POST['image']
        new_thumb = request.POST['thumb']
        new_id = 1
        images = os.listdir(os.path.join("emoface", "database", name, emotion))
        images.sort()
        for n in images:
            if n[0] == '.':
                continue
            if n[-5:] == 't.jpg':
                continue
            if int(n[:-4]) == new_id:
                new_id += 1
            else:
                break
        with open(os.path.join("emoface", "database", name, emotion, str(new_id)+".jpg"), "wb") as fh:
            fh.write(base64.b64decode(new_image))
        with open(os.path.join("emoface", "database", name, emotion, str(new_id)+"t.jpg"), "wb") as fh:
            fh.write(base64.b64decode(new_thumb))
        return HttpResponse("success")

def delete_image(request, name, emotion):
    if request.method == 'POST':
        name = name.lower()
        emotion = emotion.lower()
        image_id = request.POST['id']
        try:
        	with open(os.path.join("emoface", "database", name, emotion, ".default"), "r") as default_file:
	            default_emotion = default_file.readline()
        except FileNotFoundError as e:
        	return HttpResponse("filenot found")
        try:
        	os.remove(os.path.join("emoface", "database", name, emotion, image_id + ".jpg"))
	        os.remove(os.path.join("emoface", "database", name, emotion, image_id + "t.jpg"))
        except FileNotFoundError as e:
        	return HttpResponse("filenot found")
        if default_emotion == image_id:
            print("deleting")
            with open(os.path.join("emoface", "database", name, emotion, ".default"), "w") as default_file:
                new_default = None
                images = os.listdir(os.path.join("emoface", "database", name, emotion))
                for n in images:
                    if n[0] == '.':
                        continue
                    if n[-5:] == 't.jpg':
                        continue
                    new_default = n[:-5]
                    break
                if new_default == None:
                    copyfile(os.path.join("emoface", "default_avatar", "happy", "1.jpg"), os.path.join("emoface", "database", name, emotion, "1.jpg"))
                    copyfile(os.path.join("emoface", "default_avatar", "happy", "1t.jpg"), os.path.join("emoface", "database", name, emotion, "1t.jpg"))
                    new_default = "1"
                default_file.write(new_default)
        return HttpResponse("success")
    return HttpResponse("use POST")

def emotions(request, name, emotion):
    if request.method == 'POST':
        name = name.lower()
        emotion = emotion.lower()
        with open(os.path.join("emoface", "database", name, ".default"), "w") as default_file:
            default_file.write(emotion)
        with open(os.path.join("emoface", "database", name, emotion, ".default"), "w") as default_file:
            default_file.write(request.POST['id'])
        return HttpResponse("success")
    else:
        response = []
        images = os.listdir(os.path.join("emoface", "database", name, emotion))
        for n in images:
            if n[0] == '.':
                continue
            if n[-5:] != 't.jpg':
                continue
            with open(os.path.join("emoface", "database", name, emotion, n), "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            response.append({"id":n[:-5], "thumb":encoded_string})
        
        return JsonResponse(response, safe=False)

def new_avatar(request):
    if request.method == 'POST':
        new_avatar_thumb = request.POST['thumb']
        new_avatar_name = request.POST['name']
        new_avatar_name = new_avatar_name.strip('.')
        new_avatar_name = new_avatar_name.lower()
        avatars = os.listdir(os.path.join("emoface", "database"))
        for n in avatars:
            if n.lower() == new_avatar_name:
                return HttpResponse("avatar name exists")
        copy_tree(os.path.join("emoface", "default_avatar"), os.path.join("emoface", "database",new_avatar_name))
        with open(os.path.join("emoface", "database", new_avatar_name, "thumb.jpg"), "wb") as fh:
            fh.write(base64.b64decode(new_avatar_thumb))
    return HttpResponse("success")

def static_video(request):
    detector.stop_camera()
    with open(os.path.join("emoface", "database", ".default"), "r") as f:
        avatar_name = f.readline()
    with open(os.path.join("emoface", "database", avatar_name, ".default"), "r") as f:
        emotion = f.readline()
    with open(os.path.join("emoface", "database", avatar_name, emotion, ".default"), "r") as f:
        image_id = f.readline()
    
    with open(os.path.join("emoface", "database", avatar_name, emotion, image_id + ".jpg"), "rb") as f:
        return HttpResponse(f.read(), content_type="image/jpeg")

def dynamic_video(request):
    detector.start_camera()

    emotion = detector.detect()

    with open(os.path.join("emoface", "database", ".default"), "r") as f:
        avatar_name = f.readline()
    with open(os.path.join("emoface", "database", avatar_name, emotion, ".default"), "r") as f:
        image_id = f.readline()

    with open(os.path.join("emoface", "database", avatar_name, emotion, image_id + ".jpg"), "rb") as f:
        return HttpResponse(f.read(), content_type="image/jpeg")
    return HttpResponse("file not found")