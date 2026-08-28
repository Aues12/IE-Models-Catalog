# Wagner-Whitin Algorithm

Sade haliyle **Dynamic Lot Sizing** **(Wagner-Whitin)** akışı:

1. **Girdi al**
    
    Talep (demand), kurulum maliyeti (K), elde bulundurma maliyeti (h)
    
2. **Periyot sayısını belirle**
    
    `T = len(demand)`
    
3. **Maliyet fonksiyonunu tanımla**
    
    Bir **i** döneminde üretip **j**’ye kadar karşılama maliyeti
    
4. **DP tablosunu başlat**
    
    `F[t] = 0` ile başla (minimum maliyetler)
    
5. **İleri doğru hesapla (DP)**
    
    Her t için:
    
    - geçmiş i’leri dene
    - en düşük maliyeti seç
6. **Optimal maliyeti bul**
    
    `F[T]`
    
7. **Geri izleme (backtracking)**
    
    Hangi dönemlerde sipariş verildiğini çıkar
    
8. **Sonucu oluştur**
    
    Sipariş miktarları + toplam maliyet
    

---

## 1) DP tablosu nasıl görünüyor?

Dynamic Lot Sizing’de genelde iki şey düşünürüz:

- **C(i,j)** → *i döneminde üret, j’ye kadar karşıla* maliyeti
- **F(t)** → *t’ye kadar minimum toplam maliyet*

3 periyotluk örnek (şekil olarak):

### C(i,j) maliyet matrisi

```
        j=1    j=2    j=3
i=1     C11    C12    C13
i=2      -     C22    C23
i=3      -      -     C33
```

- Alt üçgen boş (i > j anlamsız)
- Örnek yorum:
    - C12 → 1. dönemde üretip 1 ve 2’yi karşıla
    - C13 → 1’den üret, 3’e kadar stokla

---

### F(t) (DP vektörü)

```
t:    0    1    2    3
F:    0   F1   F2   F3
```

Ve hesap:

```
F(1) = min{ F(0) + C(1,1) }

F(2) = min{
    F(0) + C(1,2),
    F(1) + C(2,2)
}

F(3) = min{
    F(0) + C(1,3),
    F(1) + C(2,3),
    F(2) + C(3,3)
}
```

---

## 2) İleri hesaplama vs geri izleme

### ➤ İleri hesaplama (forward / DP)

- Amaç: **minimum maliyeti bulmak**
- Yön: 1 → T
- Ne yapar:
    - Her t için en iyi maliyeti hesaplar
    - `F(t)` değerlerini doldurur

👉 “En ucuz planın maliyeti ne?”

---

### ➤ Geri izleme (backtracking)

- Amaç: **o maliyete nasıl ulaştığını bulmak**
- Yön: T → 0
- Ne yapar:
    - Hangi i seçildi → onu takip eder
    - Sipariş verilen dönemleri çıkarır

👉 “Hangi dönemlerde üretmeliyim?”

---

## Özet

- **C(i,j)** → lokal karar maliyetleri
- **F(t)** → global optimum maliyet
- **Forward** → hesaplar
- **Backward** → planı çıkarır

---

## Örnek veri

Küçük ve net bir örnek yapalım.

- Talep: `[10, 20, 30]`
- Kurulum maliyeti: `K = 100`
- Elde bulundurma maliyeti: `h = 1` (birim / dönem)

---

## 1) C(i,j) matrisi

Mantık: i’de üretip j’ye kadar stoklarsan →

stokta bekleyen her birim için süre × h ödersin.

### Hesaplar:

- **C11** = 100
- **C12** = 100 + (20 × 1) = 120
- **C13** = 100 + (20×1 + 30×2) = 100 + 20 + 60 = 180
- **C22** = 100
- **C23** = 100 + (30 × 1) = 130
- **C33** = 100

---

### Tablo:

```
        j=1    j=2    j=3
i=1     100    120    180
i=2      -     100    130
i=3      -      -     100
```

---

## 2) Forward (DP hesaplama)

```
F(0) = 0

F(1) = F(0) + C(1,1) = 100

F(2) = min(
    F(0) + C(1,2) = 120,
    F(1) + C(2,2) = 100 + 100 = 200
) = 120

F(3) = min(
    F(0) + C(1,3) = 180,
    F(1) + C(2,3) = 100 + 130 = 230,
    F(2) + C(3,3) = 120 + 100 = 220
) = 180
```

👉 **Minimum toplam maliyet = 180**

---

## 3) Backtracking (geri izleme)

F(3) = **180**, bu şu seçenekten geldi:

```
F(0) + C(1,3)
```

Yani:

👉 **1. dönemde üret, 3’e kadar karşıla**

---

## 4) Nihai karar

- Sipariş: sadece **1. dönemde**
- Miktar: `10 + 20 + 30 = 60`
- Diğer dönemlerde üretim yok

---

## Kısa sezgi

- Kurulum maliyeti yüksek → az sipariş ver
- Holding maliyeti düşük → stoklamak mantıklı

---