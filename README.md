# 🎭 CNN-faceFilterApp

**CNN-faceFilterApp**, Python, OpenCV ve MediaPipe kütüphanelerini kullanarak geliştirilmiş, gerçek zamanlı bir bilgisayarlı görü (Computer Vision) uygulamasıdır. Bu proje, yüz ifadelerinden duygu analizi yapar ve el hareketlerinizi (jestler) algılayarak interaktif görsel ve işitsel efektler tetikler.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-green)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Face%20%26%20Hands-orange)

## 🌟 Özellikler

### 1. Yüz ve Duygu Analizi (Face Mesh)
Yüz landmarklarını (468 nokta) analiz ederek anlık duygu durumunu tespit eder ve ekrana yansıtır:
* 😠 **Kızgın:** Kaşların çatılması ile tetiklenir (Arayüz rengi değişir).
* 😮 **Şaşkın:** Ağzın açılması (MAR oranı) ile tetiklenir.
* 😴 **Uykulu:** Göz kapaklarının kapanma oranı ile tespit edilir.
* 🙂 **Mutlu / Üzgün:** Dudak köşelerinin konumuna göre belirlenir.

### 2. Gelişmiş El Jestleri ve Efektler
El hareketlerini algılayarak özel senaryoları çalıştırır:
* 🐺 **Bozkurt İşareti:** İşaret ve serçe parmak açıkken "Kurt Uluması" sesi çalar.
* 🔫 **AK-47 Modu (Çift El Açık):** İki el havaya kaldırıldığında önce 4 saniye **Şarj** olur, ardından **Ateş** modu başlar (Görsel çizimler + Ses efekti).
* ❤️ **Kalp İşareti:** İki elin parmak uçları birleştiğinde aşk müziği çalar ve ekrana sevgi görseli yerleştirir.
* 👊 **Kavga Modu:** Yumruk çeneye yaklaştırıldığında özel ses efekti çalar ve ekranda mesaj belirir.
* 👍 **Onay/Red:** Başparmak hareketine göre ekranda "ONAY" veya "RED" mesajı verir.

### 3. Iron Man HUD Arayüzü
* Ekranın üst kısmında fütüristik bir bilgi paneli.
* Anlık parmak sayısı sayacı.
* Duruma göre renk değiştiren dinamik arayüz (Sarı, Kırmızı, Yeşil).

---

## 🛠️ Kurulum

Projenin çalışması için bilgisayarınızda Python kurulu olmalıdır.

### 1. Projeyi İndirin

```bash
git clone https://github.com/kubilaytaskafa/CNN-faceFilterApp.git
```


2. Gerekli Kütüphaneleri Yükleyin : Terminal veya komut istemcisinde şu komutu çalıştırın:


```Bash
pip install opencv-python mediapipe pygame numpy
```

3. Medya Dosyalarını Hazırlayın
Kodun hatasız çalışması ve ses/görüntü efektlerinin devreye girmesi için aşağıdaki dosyaların main.py ile aynı klasörde olması gerekir:

- Ses Dosyaları (.mp3):

- kurt_sesi.mp3

- ates_sesi.mp3

- ak47.mp3

- scarface_sesi.mp3

- ask_sesi.mp3

 Görsel Dosyaları:

- love.jpg (Alternatifler: love.jpeg )


🚀 Kullanım
Kurulum tamamlandıktan sonra uygulamayı başlatmak için:

```Bash
python proje.py
```

Uygulama tam ekran modunda açılacaktır.

Çıkış yapmak için klavyeden 'q' tuşuna basabilirsiniz.


## 🎮 Hareket Rehberi

Uygulama aşağıdaki el ve yüz hareketlerini algılayarak tepki verir:

|**Hareket**|**Nasıl Yapılır?**|**Efekt**|
|---|---|---|
|**Ateş Modu**|İki elinizi de (avuç içi açık) kameraya gösterin.|4sn sarı şarj efekti, ardından ateş ve mermi efektleri.|
|**Bozkurt**|İşaret ve serçe parmak havada, diğerleri kapalı.|Kurt uluma sesi ve gri tema.|
|**Kalp**|İki elin işaret ve baş parmaklarını birleştirin.|Aşk şarkısı ve fotoğraf overlay'i.|
|**Kavga**|Tek elinizi yumruk yapıp çenenize yaklaştırın.|"Scarface" sesi ve "ALHAMDULILLAH" yazısı.|
|**Kızgın Yüz**|Kaşlarınızı belirgin şekilde çatın.|Durum "KIZGIN" olur, arayüz yazıları kırmızılaşır.|
|**Onay (OK)**|Sadece başparmak yukarıda.|Yeşil "ONAY" yazısı.|
