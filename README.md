# TuringLab

**Sümerya Yüce** · Selçuk Üniversitesi · Bilgisayar Mühendisliği
Hesaplama Kuramı dersinin final ödevi · Mayıs 2026

Python ile yazılmış, deterministik tek şeritli bir Turing makinesi simülatörü. YAML dosyasıyla bir TM tanımlıyorsun, motor onu adım adım çalıştırıp kabul/ret, son şerit ve geçtiği adımları döndürüyor.

## Kurulum

```bash
python -m venv venv
venv\Scripts\activate         # Windows
# source venv/bin/activate    # macOS / Linux
pip install -r requirements.txt
```

Gerekenler: Python 3.10+, PyYAML, pytest.

## Kullanım

```python
from turinglab import SingleTapeTM

# Makineyi YAML dosyasından yükle
tm = SingleTapeTM.from_yaml("machines/binary_increment.yaml")

# "1011" girdisiyle çalıştır
result = tm.run(input_string="1011", verbose=True)

print(f"Sonuç Şeridi: {result.final_tape}")
print(f"Toplam Adım: {result.steps}")
print(f"Kabul mü? : {result.accepted}")
```

`verbose=True` modunda her adım el kitabındaki formata uygun şekilde basılır:

```
Adım 0 | Durum: q0 | Şerit: B[1]011B | Hareket: R
Adım 1 | Durum: q0 | Şerit: B1[0]11B | Hareket: R
...
Adım 10 | Durum: q_accept | Şerit: B[1]100B
```

## Testler

```bash
python -m pytest
```

17 test geçiyor (motor için 10, makineler için 7).

## Repo Yapısı

```
turinglab/
├── README.md           # buradasın
├── REPORT.md           # mini-rapor (Bölüm 3)
├── requirements.txt
├── turinglab/
│   ├── __init__.py
│   └── tm_engine.py    # Bölüm 1: TM motoru
├── machines/           # Bölüm 2: tasarlanan TM'ler
│   ├── binary_increment.yaml   # el kitabı örneği
│   ├── unary_to_binary.yaml
│   ├── binary_compare.yaml
│   ├── string_copy.yaml
│   └── student_choice.yaml
├── tests/
│   ├── test_tm_engine.py
│   └── test_machines.py
└── docs/
    └── design_notes.md
```

## Tasarım Kararları (Kısa)

Tek şeritli motoru `tm_engine.py` içinde tek dosya halinde tuttum. Şerit yapısını `list` yerine `dict[int, str]` ile kurdum çünkü kafa 0'ın soluna (negatif indekse) gittiğinde Python listesi yanlış davranıyor — `tape[-1]` listenin sonunu döner, sola taşma değil. Dict ile her iki yöne sonsuz şerit varmış gibi çalışıyor. Blank sembolü olarak " " yerine görünür bir karakter olan `B` seçtim, debug için kritik.

Detaylı tasarım kararları için `REPORT.md` ve `docs/design_notes.md` dosyalarına bakabilirsiniz.

## Demo Video

5–8 dakikalık ekran kaydı:
> YouTube (unlisted): _link buraya gelecek_

Videoda dört TM'in en az ikisinin verbose modda çalışması, tasarım kararlarının açıklanması ve en zor bug'ın çözümü yer alıyor.

## Notlar

- Son teslim: 22 Mayıs 2026 Cuma 23:59. Final tag'i bu tarihte oluşturulacak.
- Bonus bölümlerinden hiçbirini yapmadım, sadece zorunlu Bölüm 1+2+3 üzerinden 100 puan hedefliyorum.
