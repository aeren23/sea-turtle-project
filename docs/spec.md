# Proje Spesifikasyon Dokümanı (spec.md)
**Proje Adı:** SeaTurtle Photo-ID: Yapay Zeka Destekli Deniz Kaplumbağası Tanıma ve Takip Sistemi
**Geliştirici:** Ali Eren Oğuztaş
**Kurum:** Pamukkale Üniversitesi & DEKAMER (Kavramsal Entegrasyon)

## 1. Projenin Amacı ve Özeti
Bu projenin temel amacı, deniz kaplumbağalarının (Chelonia mydas, Caretta caretta vb.) popülasyonlarını, göç yollarını ve yaşam döngülerini takip edebilmek için zarar vermeyen (non-invasive) bir biyometrik tanımlama sistemi geliştirmektir. 

Her deniz kaplumbağasının yüzünün yan tarafında yer alan "post-ocular" (göz arkası) pul desenleri, tıpkı insanlardaki parmak izi gibi tamamen bireye özgü ve benzersizdir[cite: 1]. Bu sistem, sualtı kameralarından veya araştırmacılardan elde edilen fotoğraf verilerini kullanarak, görüntü işleme (Computer Vision) ve Derin Öğrenme (Deep Learning) algoritmaları aracılığıyla kaplumbağaların kimlik tespitini (Photo-ID) otomatik ve yüksek doğrulukla gerçekleştirmeyi hedefler[cite: 1].

## 2. Problem Tanımı
Geleneksel kaplumbağa markalama yöntemleri (plastik flipper etiketler, PIT çipleri) maliyetli olmakla kalmayıp, kaplumbağalar için travmatik olabilmekte, zamanla düşebilmekte veya okuyucu uyumsuzluğu gibi problemler yaratabilmektedir[cite: 1]. Mevcut Photo-ID yöntemleri güvenilir ve ucuz olsa da, fotoğrafların manuel olarak veya basit yazılımlarla araştırmacılar tarafından eşleştirilmesi son derece yavaş ve hata payı yüksek bir süreçtir[cite: 1]. 

Ayrıca sualtı ortamından elde edilen verilerde (yaklaşık 600 görselden oluşan çekirdek veri seti):
*   **Işık Dengesizlikleri:** Sualtı ışık kırılmaları, bulanıklık ve renk sapmaları.
*   **Açı Farklılıkları:** Kaplumbağaların kameraya olan uzaklıkları, kafa eğimleri (roll, pitch, yaw) ve perspektif farklılıkları bulunmaktadır.

## 3. Çözüm Yaklaşımı ve Sistem Mimarisi
Proje, ham fotoğrafların alınıp kimlik ID'sinin döndürüldüğü uçtan uca (end-to-end) bir yazılım sistemi olarak tasarlanmıştır. Sistem üç ana bileşenden oluşmaktadır:

### 3.1. Görüntü Ön İşleme (Preprocessing Pipeline)
*   **Yüz Tespiti (Face Detection):** Görüntüdeki gereksiz arka planı ve kaplumbağanın gövdesini atarak sadece profil yüz hattına odaklanan bir kırpma (cropping) işlemi.
*   **Açı ve Perspektif Düzeltme:** Affine dönüşümleri (Affine Transformations) kullanılarak yüz profilinin referans noktalara (örn: göz) göre standart bir yatay düzleme hizalanması.
*   **Işık ve Kontrast Optimizasyonu:** Sualtı fotoğraflarındaki gölgeleri ve ışık parlamalarını dengelemek için CLAHE (Contrast Limited Adaptive Histogram Equalization) ve maskeleme filtrelerinin uygulanması.

### 3.2. Yapay Zeka ve Sınıflandırma Modeli (AI Core)
*   Standartlaştırılmış görüntülerden özellik çıkarımı (feature extraction) yapmak üzere eğitilmiş bir Evrişimli Sinir Ağı (CNN) mimarisi (Örn: ResNet veya EfficientNet tabanlı ince ayarlı bir model).
*   Model, önceden sisteme kayıtlı olan kaplumbağaların ID'lerini bir güven skoru (confidence score) ile birlikte tahmin eder.

### 3.3. Web Platformu ve Backend
*   Kullanıcıların fotoğraf yükleyebileceği, sisteme yeni kaplumbağa kaydedebileceği veya mevcut olanları sorgulayabileceği, Clean Architecture prensiplerine uygun olarak tasarlanmış .NET 8 tabanlı bir RESTful API / Mikroservis mimarisi.
*   Yapay zeka modeli, backend sistemine bağımsız bir servis olarak entegre edilecektir.

## 4. Teknik Gereksinimler (Functional Requirements)
*   Sistem, yüklenen fotoğrafta bir kaplumbağa kafası olup olmadığını tespit edebilmelidir.
*   Sistem, yüklenen fotoğrafı otomatik olarak standardize etmeli (ışık, açı) ve modelin kabul edeceği formata (örn: 224x224 RGB) dönüştürmelidir.
*   Sistem, bilinen bir kaplumbağayı yüksek doğruluk oranı ile veri tabanındaki ID'si ile eşleştirmelidir.
*   Eşleşme bulunamazsa, sistemin bunu "Yeni/Bilinmeyen Birey" olarak raporlaması gerekmektedir.

## 5. Yazılım Kalite Gereksinimleri (Non-Functional Requirements)
Proje kod tabanı, aşağıdaki mühendislik standartlarına kesin olarak uymak zorundadır:
*   **Clean Code:** Anlaşılır, kendi kendini dökümante eden (self-documenting), sihirli sayılardan arındırılmış, modüler fonksiyonlar.
*   **SOLID Prensipleri:**
    *   Sınıflar Tek Sorumluluk Prensibi'ne (SRP) uygun tasarlanmalıdır (Görüntü okuma sınıfı ile modeli eğiten sınıf aynı olamaz).
    *   Sistem yeni modellere ve filtrelere açık, değişime kapalı (Open/Closed) olmalıdır.
    *   Bağımlılıklar (Dependency Injection) kullanılarak modüller arası gevşek bağlılık (loose coupling) sağlanmalıdır.

## 6. Veri Seti Kısıtları
*   Model eğitimi, mevcut ~600 fotoğraflık kaplumbağa veri seti ile sınırlıdır. Modelin aşırı öğrenmesini (overfitting) engellemek için veri artırımı (Data Augmentation - döndürme, renk kaydırma vb.) teknikleri uygulanacaktır.