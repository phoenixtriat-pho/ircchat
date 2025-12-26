import pyrebase
import threading
import datetime
import uuid
import getpass
import hashlib
import random
import time
from colorama import Fore, Back, Style
import colorama
from plyer import notification
import winsound
import requests
import os

def play_notification_sound():
    winsound.Beep(1000, 500) 

colorama.init(autoreset=True)
# Firebase yapılandırması
config = {
    "apiKey": "",
    "authDomain": "",
    "databaseURL": "",
    "storageBucket": ""
}
CURRENT_VERSION = "v1.1"
firebase = pyrebase.initialize_app(config)
db = firebase.database()
def check_for_updates():
    update_info = db.child("updates").get().val()

    if update_info:
        latest_version = update_info.get("latest_version")
        file_url = update_info.get("file_url")
        libraryup = update_info.get("libraryupd")
        libss = update_info.get("libs")
        if libraryup:
            print("Yeni kütüphaneler yükleniyor...")
            # libs, 'lib1', 'lib2', ... gibi key-value çiftlerinden oluşuyor
            for lib_key, lib_name in libss.items():
                print(f"Yükleniyor: {lib_name}")
                os.system(f"pip install {lib_name}")
        if latest_version and file_url and latest_version != CURRENT_VERSION:
            print(f"🚀 Yeni sürüm mevcut! ({latest_version}) Güncelleniyor...")
            download_update(file_url)
        else:
            print("✅ Yazılım güncel.")
def download_update(url):
    response = requests.get(url, allow_redirects=True)

    if response.status_code == 200:
        temp_file = "ircchat_new.py"  # Geçici yeni dosya adı
        with open(temp_file, "wb") as file:
            file.write(response.content)
        
        print("✅ Güncelleme tamamlandı! Dosyalar yenileniyor...")

        # Eski dosyayı sil
        try:
            os.remove("ircchat.py")
        except FileNotFoundError:
            print("❌ Önceki dosya bulunamadı, yeni dosya eklenecek.")

        # Yeni dosyayı doğru isimle kaydet
        os.rename(temp_file, "ircchat.py")

        print("🔄 Uygulama yeniden başlatılıyor...")
        os.system("python ircchat.py")
        exit()
    else:
        print("❌ Güncelleme başarısız oldu!")
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login():
    username = input("Kullanıcı adınızı girin: ")
    password = getpass.getpass("Şifrenizi girin: ")
    hashed_password = hash_password(password)
    users = db.child("users").get().val() or {}
    
    if username in users:
            if users[username]["password"] == hashed_password:
                if users[username]["Activation"] == True:
                    print("Giriş başarılı! Hoş geldin,", username)
                    session_id = users[username]["session_id"]
                    isAdmin = users[username].get("isAdmin", False)
                    return username, session_id, isAdmin
                else:
                    print("kullanıcı aktif değil sistem yöneticisi ile görüşün")
                    return login()     
            else:
                print("Hatalı şifre!")
                return login()
       
    else:
        print("Yeni hesap oluşturuluyor...")
        session_id = str(uuid.uuid4())
        inviteid = random.randint(1000,9999)
        isAdmin = False
        
        db.child("users").child(username).set({"password": hashed_password, "session_id": session_id, "isAdmin": False, "inviteid": inviteid,"Activation": False})
        gid = input("Yönetimden alınan Referans Kodu girilmelidir girilmeden devam edilmeyecektir ")
        if int(gid) == inviteid:
            print("Hesap oluşturuldu! Hoş geldin,", username)
            db.child("users").child(username).update({"Activation": True})
            
    
    return username, session_id, isAdmin
def generate_unique_invite_code(existing_codes):
    while True:
        new_code = str(random.randint(1000, 9999))
        if new_code not in existing_codes:
            return new_code
def join_channel():
    channels = db.child("channels").get().val() or {}
    invite_code = input("Davet kodunu girin: (yeni oluşturmak için yeni yazınız): ")
    if invite_code == "yeni":
        name = input("kanal ismi giriniz: ")
        existing_codes = {channel_data["invite_code"] for channel_data in channels.values() }
        codenew = generate_unique_invite_code(existing_codes)
        db.child("channels").child(name).set({"invite_code": codenew})
        print("Kanal başarıyla oluşturuldu davet kodunuz: " + codenew)
        return name

    else:
        for channel_name, channel_data in channels.items():
            if channel_data["invite_code"] == invite_code:
                if is_banned(channel_name, username):
                    print(Fore.RED + "🛑🛑🛑Bu kanala girişiniz yasaklandı!🛑🛑🛑")
                    return join_channel()
                print( Fore.GREEN + f"Başarıyla {channel_name} kanalına katıldınız!")
                return channel_name
    
        print("Hatalı davet kodu!")
    return join_channel()

def load_message_history(channel_name):
    thirty_minutes_ago = (datetime.datetime.now() - datetime.timedelta(minutes=30)).strftime("%H:%M:%S %d-%m-%Y")
    messages = db.child("messages").child(channel_name).get().val() or {}
    
    print("Son 30 dakikalık mesaj geçmişi:")
    for key, message in sorted(messages.items(), key=lambda x: x[1]["timestamp"]):
        if message["timestamp"] >= thirty_minutes_ago:
            print(f"[{message['timestamp']}] " + Fore.BLUE + f"{message['user']}" + Fore.LIGHTBLACK_EX + f"@{channel_name}>"+ Fore.WHITE + f"{message['text']}")

def stream_handler(message):
    data = message['data']
    if data:
        timestamp = data.get('timestamp', 'Unknown Time')
        user = data.get('user', 'Unknown User')
        text = data.get('text', '')
        if isAdmin:
            print(f"[{timestamp}] " + Fore.LIGHTRED_EX + f"{user}" + Fore.LIGHTBLACK_EX +f"@{channel_name}>" + Fore.WHITE + f" {text}")
        else:
            print(f"[{timestamp}] " + Fore.BLUE + f"{user}" + Fore.LIGHTBLACK_EX +f"@{channel_name}>" + Fore.WHITE + f" {text}")
        notification.notify(
            title=f"Yeni Mesaj - {user}",
            message=text,
            timeout=5
        )


def listen_messages(channel_name):
    db.child("messages").child(channel_name).stream(stream_handler)

def send_message(username, channel_name, text, is_alert=False):
    if text.startswith("/") and not is_alert:
        return  
    
    timestamp = datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y")
    if is_alert:
        text = Fore.RED + f"[@ALERT]🛑🛑 - {text} - 🛑🛑[@ALERT]"
    db.child("messages").child(channel_name).push({"user": username, "text": text, "timestamp": timestamp})
def activeusers():
    timestamp = int(time.time())  # Unix timestamp olarak kaydet
    db.child("actives").child(channel_name).child(username).set({"timestamp": timestamp})
def unactive():
    db.child("actives").child(channel_name).child(username).set(False)
def activelist():
    users = db.child("actives").child(channel_name).get().val() or {}
    current_time = int(time.time())
    
    print(Fore.CYAN + "Aktif kullanıcılar:")
    for user, data in users.items():
        last_active = data.get("timestamp", 0)
        if current_time - last_active <= 60:  # Son 60 saniyede aktif olanlar listelensin
            print(f"- " +  user)
        else:
            db.child("actives").child(channel_name).child(user).remove()
def heartbeat(username, channel_name):
    while True:
        activeusers()
        time.sleep(30)
def ban_user(admin, channel_name, target_user):
    if not isAdmin:
        print(Fore.RED + "Bu komutu kullanma yetkiniz yok!")
        return
    
    # Kullanıcıyı ban listesine ekle
    db.child("bans").child(channel_name).child(target_user).set(True)

    # Kullanıcıyı aktif listesinden çıkar (kanaldan atma)
    db.child("actives").child(channel_name).child(target_user).remove()

    # Kullanıcıyı zorla çıkarmak için sinyal gönder
    db.child("ban_signals").child(channel_name).child(target_user).set(True)

    print(f"{target_user} kullanıcısı {channel_name} kanalından banlandı!")
    send_message(admin, channel_name, f"{target_user} kanaldan yasaklandı.", is_alert=True)
def is_banned(channel_name, username):
    banned_users = db.child("bans").child(channel_name).get().val() or {}
    return username in banned_users
def check_ban_status(username, channel_name):
    while True:
        time.sleep(5)  # 5 saniyede bir kontrol et
        if is_banned(channel_name, username):
            print(Fore.YELLOW + "\n⚠️ Bu kanaldan yasaklandınız! Başka bir kanal seçmelisiniz.\n")
            unactive()
            channel_name = join_channel()
            load_message_history(channel_name)
            threading.Thread(target=listen_messages, args=(channel_name,), daemon=True).start()

if __name__ == "__main__":
    check_for_updates()
    username, session_id, isAdmin = login()
    
    
    
    channel_name = join_channel()
    
    activeusers()
    threading.Thread(target=heartbeat, args=(username, channel_name), daemon=True).start()
    threading.Thread(target=check_ban_status, args=(username, channel_name), daemon=True).start()
    load_message_history(channel_name)
    threading.Thread(target=listen_messages, args=(channel_name,), daemon=True).start()
    while True:
        msg = input("Mesaj: ")
        if msg == "/exit":
            channel_name = join_channel()
            unactive()
            load_message_history(channel_name)
            threading.Thread(target=listen_messages, args=(channel_name,), daemon=True).start()
        if msg == "/list":
            if isAdmin:
                activelist()
            else:
                print(Fore.RED + "bu komutu kullanmak için admin yetkilerine ihtiyacın var")   
        if msg.startswith("/ban "):
            if isAdmin:
                target_user = msg.split(" ")[1]
                ban_user(username, channel_name, target_user)
            else:
                print(Fore.RED + "bu komutu kullanmak için admin yetkilerine ihtiyacın var")   
        
        if msg.startswith("/alert "):  # Eğer mesaj /alert ile başlıyorsa
            if isAdmin:

                alert_msg = msg[7:]  # "/alert " kısmını kaldır
                send_message(username, channel_name, alert_msg, is_alert=True)
            else:
                print(Fore.RED + "bu komutu kullanmak için admin yetkilerine ihtiyacın var")
        else:
            send_message(username, channel_name, msg)