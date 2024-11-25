from django.shortcuts import render, redirect
import cv2
import face_recognition
import numpy as np
from django.http import JsonResponse, StreamingHttpResponse


def load_and_encode_images(image_files):
    known_face_encodings = []
    
    for image_file in image_files:
        img = face_recognition.load_image_file(image_file)
        face_encodings = face_recognition.face_encodings(img)
        
        if face_encodings:
            known_face_encodings.append(face_encodings[0].tolist())  
    
    return known_face_encodings

def generate_frames(known_face_encodings):
    video_capture = cv2.VideoCapture(0)
    known_face_encodings = [np.array(encoding) for encoding in known_face_encodings]  

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        flipped_frame = cv2.flip(frame, 1)
        face_video_locations = face_recognition.face_locations(flipped_frame)

        if face_video_locations:
            face_video_encodings = face_recognition.face_encodings(flipped_frame, face_video_locations)

            for face_encoding, (top, right, bottom, left) in zip(face_video_encodings, face_video_locations):
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

                if True in matches:
                    cv2.rectangle(flipped_frame, (left, top), (right, bottom), (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', flipped_frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def main(request):
    if request.method == 'POST':
        image_files = request.FILES.getlist('image')
        if image_files:
            known_face_encodings = load_and_encode_images(image_files)
            request.session['known_face_encodings'] = known_face_encodings
            return redirect('main')
    known_face_encodings = request.session.get('known_face_encodings', [])
    return render(request, 'main.html', {'known_face_encodings': known_face_encodings})

def video_feed(request):
    known_face_encodings = request.session.get('known_face_encodings', [])
    return StreamingHttpResponse(generate_frames(known_face_encodings), content_type='multipart/x-mixed-replace; boundary=frame')

def clear_session(request):
    request.session.pop('known_face_encodings', None)
    return JsonResponse({'status': 'session cleared'})