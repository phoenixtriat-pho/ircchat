# IRC Chat — readme

Kısa açıklama
- Basit Firebase tabanlı konsol IRC benzeri sohbet istemcisi (Windows için). Kanal/davet kodu, aktif kullanıcı takibi, admin yetkileri ve güncelleme kontrolü içerir.

Gereksinimler
- Python 3.8+
- Windows (winsound kullanımı; Linux/Mac için ses kodu değiştirilmeli)
- Python paketleri:
    - pyrebase
    - colorama
    - plyer
    - requests

Kurulum
1. Depoyu veya dosyayı kopyalayın (ana dosya: ircchat.py).
2. Gerekli paketleri yükleyin:
     pip install pyrebase4 colorama plyer requests
3. Firebase yapılandırmasını ircchat.py içindeki `config` sözlüğüne doldurun:
     - apiKey, authDomain, databaseURL, storageBucket

Nasıl çalıştırılır
- Komutu çalıştırın:
    python ircchat.py

Özellikler
- Kullanıcı yönetimi
    - Yeni kullanıcı oluşturma; şifreler SHA-256 ile hash'lenir.
    - Hesap aktivasyonu: invite id ile doğrulama (basit doğrulama akışı).
- Kanallar ve davet kodları
    - Kanal oluşturma: "yeni" girilerek kanal adı ve benzersiz 4 haneli davet kodu oluşturulur.
    - Davet kodu ile kanala katılma.
- Mesajlaşma
    - Gerçek zamanlı mesaj akışı Firebase Realtime Database ile stream edilir.
    - Son 30 dakikanın mesaj geçmişi yüklenir.
    - Lokal bildirim (plyer) ve ses bildirimi (winsound).
- Aktif kullanıcı takibi
    - Periyodik "heartbeat" ile kullanıcı aktifliği kayıt edilir; 60 saniyeden eski kullanıcılar temizlenir.
- Ban ve yönetici (admin) yetkileri
    - Adminler `/ban <kullanici>` ile ban atabilir; ban sinyali gönderilir.
    - Banlı kullanıcı kanala girişte engellenir.
- Güncelleme denetimi
    - `updates` düğümünden `latest_version`, `file_url`, `libraryupd`, `libs` kontrol edilir; gerekirse yeni sürüm indirilir ve pip ile kütüphane yüklenir, ircchat.py yenilenip çalıştırılır.

Kullanım — Komutlar
- Mesaj yazıp Enter: normal mesaj gönderir.
- /exit — kanaldan çıkıp başka kanala geçer.
- /list — (sadece admin) aktif kullanıcıları listeler.
- /ban <kullanici> — (sadece admin) hedef kullanıcıyı banlar.
- /alert <metin> — (sadece admin) uyarı mesajı olarak gönderir (kırmızı vurgulu).

Firebase veri yapısı (örnek)
- users/{username}:
    - password, session_id, isAdmin, inviteid, Activation
- channels/{channelName}:
    - invite_code
- messages/{channelName}:
    - push edilmiş mesaj objeleri {user, text, timestamp}
- actives/{channelName}/{user}: { timestamp }
- bans/{channelName}/{user}: true
- updates: { latest_version, file_url, libraryupd, libs: { lib1: "paket" ... } }

Güvenlik notları
- Şifreler SHA-256 ile saklanır (salt yok). Gerçek uygulamalarda salt, bcrypt/argon2 ve güvenli kimlik doğrulama önerilir.
- Güncelleme mekanizması HTTP ile kod indirdiği için doğrulama/imanet kontrolü yok; üretimde imzalama veya güvenli dağıtım önerilir.
- Davet / admin mantığı basit ve güvenlik açısından zayıf olabilir; üretim için yetki kontrolleri güçlendirilmeli.

Sorun giderme
- Firebase bağlantı hatası: config doğru mu, internet var mı kontrol edin.
- Bildirim/ ses çalışmıyorsa sistem izinleri ve Windows ortamını kontrol edin.

Lisans
- Bu proje örnek amaçlıdır. Üretim kullanımı öncesi güvenlik ve hata kontrolleri yapılmalıdır.