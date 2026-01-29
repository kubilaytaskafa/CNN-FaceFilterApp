import cv2
import mediapipe as mp
import math
import numpy as np
from collections import deque
import time
import pygame
import os

# ---------------------------------------------------------
# 1. TEMEL AYARLAR
# ---------------------------------------------------------
pygame.mixer.init()

current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Calisma Klasoru: {current_dir}")

# --- DOSYA OKUMA VE SES ---
def read_image_safe(path):
    try:
        with open(path, "rb") as f:
            bytes = bytearray(f.read())
            numpyarray = np.asarray(bytes, dtype=np.uint8)
            img = cv2.imdecode(numpyarray, cv2.IMREAD_COLOR)
            return img
    except Exception as e:
        return None

def load_sound_safe(filename):
    path = os.path.join(current_dir, filename)
    if os.path.exists(path):
        return pygame.mixer.Sound(path)
    return None

# Sesleri Yükle
sound_howl = load_sound_safe("kurt_sesi.mp3")
sound_charge = load_sound_safe("ates_sesi.mp3")
sound_ak47 = load_sound_safe("ak47.mp3")
sound_fight = load_sound_safe("scarface_sesi.mp3")
sound_love = load_sound_safe("ask_sesi.mp3")

# Ses Seviyeleri
if sound_charge: sound_charge.set_volume(1.0)
if sound_ak47: sound_ak47.set_volume(1.0)

# Fotoğraf Yükle (love.jpg öncelikli)
photo_variations = ["love.jpg", "love.jpeg"]
heart_photo_original = None

for p_name in photo_variations:
    full_path = os.path.join(current_dir, p_name)
    if os.path.exists(full_path):
        heart_photo_original = read_image_safe(full_path)
        if heart_photo_original is not None: 
            print(f"Fotograf Yuklendi: {p_name}")
            break

# ---------------------------------------------------------
# 2. YARDIMCI FONKSİYONLAR
# ---------------------------------------------------------
def manage_sound(sound_obj, should_play, is_loop=False):
    if sound_obj is None: return
    if should_play:
        if sound_obj.get_num_channels() == 0:
            sound_obj.play(-1 if is_loop else 0)
    else:
        if sound_obj.get_num_channels() > 0:
            sound_obj.fadeout(300)

def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def overlay_image_fixed(bg_img, overlay_img, offset_y_ratio=0.75):
    if overlay_img is None: return bg_img
    h_bg, w_bg, _ = bg_img.shape
    h_ov, w_ov, _ = overlay_img.shape
    center_x = w_bg // 2
    center_y = int(h_bg * offset_y_ratio) 
    top_x, top_y = center_x - (w_ov // 2), center_y - (h_ov // 2)
    y1, y2 = max(0, top_y), min(h_bg, top_y + h_ov)
    x1, x2 = max(0, top_x), min(w_bg, top_x + w_ov)
    ov_y1, ov_y2 = max(0, -top_y), max(0, -top_y) + (y2 - y1)
    ov_x1, ov_x2 = max(0, -top_x), max(0, -top_x) + (x2 - x1)
    if (y2 > y1) and (x2 > x1):
        bg_img[y1:y2, x1:x2] = overlay_img[ov_y1:ov_y2, ov_x1:ov_x2]
    return bg_img

# ---------------------------------------------------------
# 3. BAŞLATMA
# ---------------------------------------------------------
cap = cv2.VideoCapture(0)
window_name = "IRON MAN HUD - ANGRY MODE"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

mp_face = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

face_mesh = mp_face.FaceMesh(max_num_faces=1, refine_landmarks=True)
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

emotion_history = deque(maxlen=15)

# --- ZAMANLAMA AYARLARI ---
last_repulsor_time = 0 
charge_duration = 4.0  # Şarj
fire_duration = 3.0    # Ateş
total_cycle_time = charge_duration + fire_duration # Toplam 7 sn

# ---------------------------------------------------------
# 4. ANA DÖNGÜ
# ---------------------------------------------------------
while True:
    success, img = cap.read()
    if not success: continue

    img = cv2.flip(img, 1)
    h, w, c = img.shape
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    current_time = time.time()

    # --- UI TASARIMI (ÜST PANEL) ---
    header_h = int(h * 0.15)
    fs_base = w / 1000.0
    
    cv2.rectangle(img, (0, 0), (w, header_h), (15, 15, 15), cv2.FILLED)
    cv2.line(img, (0, header_h), (w, header_h), (0, 255, 255), 2)
    cv2.line(img, (int(w*0.3), 0), (int(w*0.3), header_h), (50, 50, 50), 2)
    cv2.line(img, (int(w*0.7), 0), (int(w*0.7), header_h), (50, 50, 50), 2)

    # Durum Değişkenleri
    top_panel_gesture_text = "TARAMA..." 
    top_panel_color = (200, 200, 200)   
    
    total_fingers = 0
    wolf_active = False 
    fight_active = False
    charge_active = False
    ak47_active = False 
    love_active = False
    chin_point = None
    face_width_pixel = 0
    hands_data = [] 

    # --- 1. YÜZ ANALİZİ (FULL SENSÖR & DUYGU) ---
    face_results = face_mesh.process(img_rgb)
    current_emotion = "TANIMSIZ"
    
    if face_results.multi_face_landmarks:
        for face in face_results.multi_face_landmarks:
            mp_draw.draw_landmarks(img, face, mp_face.FACEMESH_TESSELATION, None, mp_drawing_styles.get_default_face_mesh_tesselation_style())
            mp_draw.draw_landmarks(img, face, mp_face.FACEMESH_CONTOURS, None, mp_drawing_styles.get_default_face_mesh_contours_style())

            lm = face.landmark
            def get_pt(idx): return (int(lm[idx].x * w), int(lm[idx].y * h))
            chin_point = get_pt(152)
            face_width_pixel = distance(get_pt(234), get_pt(454))

            # --- DUYGU MATEMATİĞİ ---
            
            # 1. Dudak Açıklığı (Şaşkınlık)
            mouth_w = distance(get_pt(61), get_pt(291))
            mar = distance(get_pt(13), get_pt(14)) / mouth_w if mouth_w > 0 else 0
            
            # 2. Göz Kapalılığı (Uykulu)
            left_eye = distance(get_pt(159), get_pt(145))
            right_eye = distance(get_pt(386), get_pt(374))
            avg_eye = (left_eye + right_eye) / 2.0

            # 3. Dudak Köşeleri (Mutlu/Üzgün)
            corners_y = (lm[61].y + lm[291].y) / 2
            center_y = (lm[13].y + lm[14].y) / 2

            # 4. YENİ: KAŞ ÇATMA (KIZGINLIK)
            # 107 (Sol iç kaş) ve 336 (Sağ iç kaş) arası mesafe
            brow_inner_dist = distance(get_pt(107), get_pt(336))
            
            # Eşik Değerler
            emotion = "NORMAL"
            
            # Mantık Sırası: Önce belirgin olanlar
            if mar > 0.35: 
                emotion = "SASKIN" 
            elif brow_inner_dist < face_width_pixel * 0.16: # Normalde ~0.20-0.25 arasıdır
                emotion = "KIZGIN"
            elif corners_y < center_y - 0.015: 
                emotion = "MUTLU"
            elif corners_y > center_y + 0.015: 
                emotion = "UZGUN"
            elif avg_eye < face_width_pixel * 0.04: 
                emotion = "UYKULU"
            
            emotion_history.append(emotion)
            current_emotion = max(set(emotion_history), key=emotion_history.count)

    # --- 2. EL ANALİZİ ---
    hand_results = hands.process(img_rgb)
    
    if hand_results.multi_hand_landmarks:
        for i, hand_lms in enumerate(hand_results.multi_hand_landmarks):
            lm_list = []
            for id, lm in enumerate(hand_lms.landmark):
                lm_list.append([id, int(lm.x * w), int(lm.y * h)])
            
            cx, cy = lm_list[9][1], lm_list[9][2]
            
            fingers = []
            tip_ids = [4, 8, 12, 16, 20]
            if abs(lm_list[4][1] - lm_list[9][1]) > abs(lm_list[3][1] - lm_list[9][1]): fingers.append(1)
            else: fingers.append(0)
            for id in range(1, 5):
                if lm_list[tip_ids[id]][2] < lm_list[tip_ids[id]-2][2]: fingers.append(1)
                else: fingers.append(0)
            
            hand_fingers_count = fingers.count(1)
            total_fingers += hand_fingers_count
            
            hands_data.append({"fingers": fingers, "count": hand_fingers_count, "landmarks": lm_list, "center": (cx, cy)})

            # -- TEK EL JESTLERİ --
            if fingers == [1, 0, 0, 0, 0]: # Sadece başparmak açık
                if lm_list[4][2] < lm_list[2][2]: 
                    top_panel_gesture_text = "ONAY (OK)"
                    top_panel_color = (0, 255, 0) # Yeşil
                else: 
                    top_panel_gesture_text = "RED (NO)"
                    top_panel_color = (0, 0, 255) # Kırmızı
            
            # Kurt
            if fingers[1] == 1 and fingers[4] == 1 and fingers[2] == 0 and fingers[3] == 0:
                wolf_active = True
                top_panel_gesture_text = "BOZKURT"
                top_panel_color = (128, 128, 128)

            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)

    # --- 3. ÇOKLU EL MANTIĞI ---
    open_palm_count = 0
    for h_data in hands_data:
        if h_data["count"] == 5: open_palm_count += 1

    # A) ATEŞ (AK-47) - İki El Açık
    if open_palm_count == 2:
        if current_time - last_repulsor_time > total_cycle_time + 0.5:
            last_repulsor_time = current_time
        
        time_passed = current_time - last_repulsor_time
        overlay = img.copy()

        for h_data in hands_data:
            hcx, hcy = h_data["center"]
            if time_passed < charge_duration:
                # ŞARJ (4 Saniye)
                charge_active = True
                top_panel_gesture_text = f"SARJ: {int(charge_duration - time_passed)}s"
                top_panel_color = (0, 255, 255) # Sarı
                
                radius = int(20 + (time_passed / charge_duration) * 40)
                cv2.circle(overlay, (hcx, hcy), radius, (0, 255, 255), cv2.FILLED)
            elif time_passed < total_cycle_time:
                # ATEŞ (3 Saniye)
                ak47_active = True
                top_panel_gesture_text = "!!! ATES !!!"
                top_panel_color = (0, 0, 255) # Kırmızı
                
                cv2.circle(overlay, (hcx, hcy), 90, (0, 0, 255), cv2.FILLED)
                for _ in range(3):
                    x_rnd = int(hcx + np.random.randint(-80, 80))
                    y_rnd = int(hcy - 500)
                    cv2.line(img, (hcx, hcy), (x_rnd, y_rnd), (0, 255, 255), 3)

        cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)

    # B) KALP (AŞK) - İki El Kalp Şekli
    elif len(hands_data) == 2 and not charge_active and not ak47_active and not wolf_active:
        h1, h2 = hands_data[0], hands_data[1]
        p1, p2 = h1["landmarks"][8], h2["landmarks"][8]
        t1, t2 = h1["landmarks"][4], h2["landmarks"][4]
        
        if distance(p1, p2) < 70 and distance(t1, t2) < 70:
            love_active = True
            top_panel_gesture_text = "KALP <3"
            top_panel_color = (0, 0, 255) # Kırmızı
            
            if heart_photo_original is not None:
                target_h = int(h * 0.4) 
                ratio = target_h / heart_photo_original.shape[0]
                target_w = int(heart_photo_original.shape[1] * ratio)
                resized_photo = cv2.resize(heart_photo_original, (target_w, target_h))
                img = overlay_image_fixed(img, resized_photo, offset_y_ratio=0.75)

    # C) KAVGA
    if chin_point is not None and len(hands_data) > 0:
        for h_data in hands_data:
            if h_data["fingers"][1:] == [0,0,0,0] and distance(h_data["center"], chin_point) < face_width_pixel * 1.5:
                fight_active = True
                top_panel_gesture_text = "KAVGA MODU"
                top_panel_color = (255, 0, 255)

    # SESLER
    manage_sound(sound_howl, wolf_active, is_loop=True)
    manage_sound(sound_fight, fight_active, is_loop=True)
    manage_sound(sound_love, love_active, is_loop=True)
    manage_sound(sound_charge, charge_active, is_loop=False) 
    manage_sound(sound_ak47, ak47_active, is_loop=True)

    # --- DASHBOARD YAZILARI ---
    
    # 1. SOL PANEL: DUYGU
    cv2.putText(img, "DURUM:", (20, int(header_h * 0.4)), cv2.FONT_HERSHEY_SIMPLEX, fs_base*0.7, (150,150,150), 1)
    
    # Eğer Kızgınsa rengi Kırmızı yap, değilse Yeşil
    emotion_color = (0, 0, 255) if current_emotion == "KIZGIN" else (0, 255, 0)
    cv2.putText(img, current_emotion, (20, int(header_h * 0.8)), cv2.FONT_HERSHEY_SIMPLEX, fs_base*1.2, emotion_color, 2)

    # 2. ORTA PANEL: PARMAK SAYISI
    title = f"PARMAK SAYISI: {total_fingers}"
    t_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, fs_base, 2)[0]
    cv2.putText(img, title, (int(w/2 - t_size[0]/2), int(header_h * 0.65)), cv2.FONT_HERSHEY_SIMPLEX, fs_base, (255, 255, 255), 2)

    # 3. SAĞ PANEL: JEST ÇIKTISI
    g_size = cv2.getTextSize(top_panel_gesture_text, cv2.FONT_HERSHEY_SIMPLEX, fs_base*1.2, 2)[0]
    g_x = int(w * 0.95) - g_size[0] 
    cv2.putText(img, top_panel_gesture_text, (g_x, int(header_h * 0.7)), cv2.FONT_HERSHEY_SIMPLEX, fs_base*1.2, top_panel_color, 2)

    if fight_active:
        msg = "ALHAMDULILLAH!!!!"
        t_size = cv2.getTextSize(msg, cv2.FONT_HERSHEY_COMPLEX, fs_base*2, 3)[0]
        cv2.putText(img, msg, (int((w-t_size[0])/2), int(h/2)), cv2.FONT_HERSHEY_COMPLEX, fs_base*2, (255, 255, 255), 3)

    cv2.imshow(window_name, img)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()
