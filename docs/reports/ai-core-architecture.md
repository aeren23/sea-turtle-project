📷 Ham Fotoğraf (herhangi bir açı)
        │
   ┌────▼─────────────────────────────────┐
   │  1. HeadDetector (YOLOv8-Nano)       │
   │     • Kafayı bulur → bbox [x,y,w,h]  │
   │     • Yönü tahmin eder → "left"       │
   │     • Güven skoru → 0.76              │
   └────┬─────────────────────────────────┘
        │ bbox
   ┌────▼─────────────────────────────────┐
   │  2. TurtlePreprocessingPipeline      │
   │     • bbox ile crop (kafayı kes)     │
   │     • 224×224'e resize               │
   │     • CLAHE (kontrast dengeleme)     │
   │     • Underwater color correction    │
   └────┬─────────────────────────────────┘
        │ temiz 224×224 görsel
   ┌────▼─────────────────────────────────┐
   │  3. EmbeddingExtractor (ResNet-50)   │
   │     • Görsel → 512-d float vektör    │
   │     • L2 normalize (birim uzunluk)   │
   └────┬─────────────────────────────────┘
        │ 512-d embedding
   ┌────▼─────────────────────────────────┐
   │  4. FAISS Fallback Search            │
   │     • faiss_left'te ara → sonuçlar   │
   │     • faiss_right'ta ara → sonuçlar  │
   │     • faiss_top'ta ara → sonuçlar    │
   │     • Hepsini skora göre sırala      │
   │     • En iyi top-5'i döndür          │
   └────┬─────────────────────────────────┘
        │
   ┌────▼─────────────────────────────────┐
   │  5. Karar                            │
   │     • skor ≥ 0.6 → "BİLİNEN: t042"  │
   │     • skor < 0.6 → "BİLİNMEYEN"     │
   └──────────────────────────────────────┘