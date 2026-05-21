# TuringLab Mini-Rapor

**Sümerya Yüce**
Selçuk Üniversitesi · Bilgisayar Mühendisliği
Hesaplama Kuramı · TuringLab Final Ödevi · Mayıs 2026

---

## 1. Giriş

TuringLab, dersin final ödevi için yazdığım küçük bir Turing makinesi simülatörü. Python'da yazdım. Kullanıcı bir YAML dosyasıyla deterministik tek şeritli bir TM tanımlıyor, motor o makineyi adım adım çalıştırıp kabul/ret, son şerit ve geçtiği adımları döndürüyor.

Amaç sınıfta tahta üstünde gördüğümüz "soldan sağa kafa hareketi, δ tablosu" gibi şeyleri elime alıp çalıştırabilmekti. Hocanın el kitabındaki `binary_increment` örneği ilk çalıştırdığım makineydi, motoru onun üstünde geliştirdim.

Repo iki ana parçadan oluşuyor: `turinglab/` paketi motoru içeriyor (tek dosya, `tm_engine.py`), `machines/` klasörü ise 4 farklı TM YAML'ını barındırıyor. Bölüm 2 kapsamında dört makine tasarladım: unary→binary çevirici, binary karşılaştırma, dizgi kopyalama ve 4'e bölünebilirlik testi. Testleri `tests/` altında topladım, `pytest` çalıştırınca 17 test geçiyor.

Bu raporda mimari kararlarımı, dört makineyi kısaca anlatacağım, sonra da "Bir TM'in dilini başka bir TM tanısın diye TuringLab nasıl genişletilebilir?" sorusunu işleyeceğim.

## 2. Mimari ve Tasarım Kararları

Mimari kısmı çok süslü değil çünkü Bölüm 1 zaten "tek dosya, iki ana sınıf" istiyor. Onun için motoru `tm_engine.py` içinde tutup şu sınıfları yazdım:

- `SingleTapeTM`: ana motor. `from_yaml` ile YAML'dan yükleme, `_validate` ile kontrol, `run` ile çalıştırma.
- `Tape`: şerit, kafa pozisyonu, okuma/yazma.
- `Configuration`: her adımdaki anlık görüntü (state, tape, head). `frozen=True` çünkü değişmemesi gerek.
- `Transition`: tek bir δ kuralı. L/R dışında bir hareket yönü girilirse `__post_init__` patlatıyor.
- `RunResult`: motorun döndürdüğü sonuç paketi. `accepted`, `reason`, `final_tape`, `steps`, `history`.

### Şeridi nasıl temsil ettim?

Bu en çok düşündüğüm karardı. Liste yerine `dict[int, str]` kullandım. Sebep: kafa pozisyonu negatife düşünce Python listesi yanlış davranıyor — `tape[-1]` listenin sonunu döner, gerçek "sola taşma" değil. El kitabında "Karar size ait" diyen bir madde vardı; ben sola taşma olunca da makine çalışmaya devam etsin istedim. Dict ile her iki yöne sonsuz şerit varmış gibi davranıyor, blank olan hücreleri hiç saklamıyorum. Yazma sırasında hücreye blank yazılırsa dict'ten siliyorum, bu sayede şerit gereksiz büyümüyor.

İkinci bir karar blank sembolü için "B" karakterini kullanmaktı. El kitabında uyarı vardı, " " (boşluk) seçenler debug'da kaybolurmuş — ben görünür bir harf koydum.

### YAML doğrulaması

Başta sadece blank ve accept_states'i kontrol ediyordum. Sonra "bozuk YAML'a karşı dayanıklı ol" maddesi için doğrulamayı biraz genişlettim. Şu an `_validate` şunları kontrol ediyor:

- accept_states ve reject_states states içinde olmalı
- input_alphabet, tape_alphabet'in alt kümesi olmalı
- Her geçiş kuralının kaynak/hedef durumu ve okunan/yazılan sembolü tanımlı olmalı
- Aynı (durum, sembol) ikilisi için iki kural varsa deterministik olmaz → hata

Bu sonuncuyu eklediğimde eski YAML'ımdaki bir hatayı yakaladım: aynı geçişi iki kez yazmışım, ikinci tanım birinciyi sessizce eziyordu. Tipik "neden farklı çıktı veriyor lan bu" bug'ı.

### `run()` döngüsü

Çalıştırma kısmı düz bir while döngüsü. Her iterasyonda önce state'in accept/reject olup olmadığına bakıyorum, sonra (state, read) için kural arıyorum, kural yoksa "no_transition" diye dönüyorum. Verbose modda her adımı el kitabındaki formata uygun basıyorum:

```
Adım 5 | Durum: q_back | Şerit: B101[1]B | Hareket: L
```

Burada "Hareket" alanı bir sonraki adımın yönü; kullanıcının "kafa şimdi şuradan oraya gidecek" şeklinde okuması daha doğal. Bunu önce yanlış yazmıştım, Adım 0'da Hareket alanını basmıyordum, sonra el kitabındaki örnekte de Adım 0 satırında Hareket olduğunu fark edip düzelttim.

History için her transition'dan sonra Configuration ekliyorum, başlangıç da dahil → uzunluk her zaman `steps + 1` oluyor. Bunu test ediyorum çünkü el kitabında "23 adım, 24 history" denmiş.

## 3. Tasarlanan TM'ler

### TM-1: Unary → Binary

Stratejim iki tane `X` işaretçisi kullanmak oldu. Sol `X`'in soluna ikili sayaç koyup iki `X` arası kalan tüketilmemiş `1`'leri tek tek silerek sayacı bir bir artırdım. Hocanın el kitabındaki `{1, 0, B, X}` alfabe sınırına da uydu.

En çok zorlandığım yer sayacın yönüydü. Önce sayacı sağ tarafa koymayı denedim ama taşma olunca başa bit eklemek gerekiyor, çok karışıyor. Sola alınca sorun kayboldu — sayaç doğal olarak sola doğru büyüyebiliyor. Bu makinede 8 durum çıktı, biraz fazla ama her durumun adı net iş yapıyor (q_find, q_inc, q_cleanup_left gibi). Daha az ile yazılabilir ama okunabilirliği bozardı.

### TM-2: İkili Karşılaştırma

`w1#w2` formundaki iki binary sayıyı karşılaştırıyor, w1 > w2 ise kabul. Önce uzunlukları eşliyorum (her soldaki bit için sağda da bir bit işaretliyorum, A/C ve D/E ile), uzunluklar farklıysa sonuç doğrudan belli. Eşitse işaretleri eski haline getirip soldan sağa bit-bit karşılaştırıyorum. 16 durum çıktı çünkü uzunluk kıyaslamasıyla bit kıyaslamasını ayrı durumlarda tutmak hata yapmamı engelledi.

Tek şeritte yapmak gerçekten çok ileri-geri tarama gerektiriyor. Hocanın el kitabında "bu kadar kafa hareketi yerine 2 şerit kullansaydım daha kolay olurdu diye düşüneceksiniz" notu birebir benim halim oldu — multi-tape bonus'unu yapsaydım bu makine yarı yarıya kısalırdı.

### TM-3: Dizgi Kopyalama

`abba` → `abba#abba`. Önce girdinin sonuna `#` koydum. Sonra sırasıyla her `a` veya `b` karakterini büyük harf (A/C) işaretçiye dönüştürüp bandın sonuna gidip karşılığını ekledim. İşim bitince A/C'leri tekrar a/b yaptım. 7 durum yeterli oldu çünkü iş zaten net evrelere ayrılıyor: sona git, başa dön, işaretle, ekle, geri yükle, kabul et.

Boş girdi durumu epey kafamı karıştırdı. `w#w` formülünde w boş olsa bile `#` kalmalı, yani çıktısı `#` olmalı. Bunu testte özellikle kontrol ediyorum çünkü ilk yazımda boş girdiyi yanlış çözmüştüm.

### TM-4 (Öğrenci Seçimi): 4'e Bölünebilirlik

Listedeki seçeneklerden (a)'yı seçtim. Normalize ikili gösterimde bir sayının 4'e bölünebilir olması için ya tam olarak `0` olması ya da son iki bitinin `00` olması yeterli. Bu yüzden bu TM aslında küçük bir DFA gibi davranıyor: sağa doğru ilerlerken son iki bitin durumlarını state'lerde tutuyor (q_last0, q_last1, q_suffix00 vs.). Ek işaretçi sembole gerek olmadı, alfabe yalnızca `{0, 1, B}`. 8 durum çıktı, daha azla yapmak mümkün ama isimler mantığı açık gösteriyor.

En önemli hata ayıklama noktası `0` ile `10` girdilerini ayırmaktı. Teorik olarak 0 sayısı 4'e bölünür, bu yüzden `0` kabul, `10` ve boş girdi ret. Bunu ayırmak için `q_single0` ayrı bir durum oldu.

## 4. Kavramsal Tartışma — UTM Genişletmesi

Soruyu (b) seçtim: bir TM'in dilini başka bir TM tarafından tanımak için TuringLab nasıl genişletilebilir?

Klasik UTM şöyle çalışır: girdisi iki parçadan oluşur, bir TM'in kodlaması ⟨M⟩ ile birlikte M'nin gerçek girdisi w. UTM, M(w) ne yapacaksa onu adım adım taklit eder. TuringLab'i UTM olarak kullanabilmek için yapmam gereken birkaç şey var.

İlk olarak bir TM'in kodlamasını şerit üzerinde temsil etmem lazım. Şu an `SingleTapeTM` Python nesnesi olarak yaşıyor, YAML'dan okunup veri yapısına dönüşüyor. UTM senaryosunda bu yapının kendisini bant üzerinde bir string olarak temsil etmem gerek. Bunun için basit bir kodlama şeması seçeceğim — mesela her durum `q` öneki + binary indeks, geçişler `;` ayraçlı (`q0,0,q1,1,R;q0,1,q0,0,R;...`). UTM'nin başlangıç şeridi şu olur: `[encode(M)] # [w]`.

İkinci ihtiyaç: UTM'in kendisi de bir TM olduğu için onu da YAML olarak yazmam lazım. Tek şeritli bir UTM çok karmaşık olur, δ kuralları kolayca yüzleri bulur. Pratik açıdan UTM'i **çok şeritli** yapmak çok daha mantıklı: bir şerit M'in kodlamasını, bir şerit M'in mevcut durumunu, bir şerit gerçek girdiyi (yani M'in çalıştığı simüle bandı) tutar. Yani UTM doğal olarak Bonus A'nın (multi-tape) üstüne kuruluyor — önce çok şeritli motoru yazmam gerek.

Üçüncü ihtiyaç motor düzeyinde değil aslında. UTM zaten "bir TM"; benim motorum onu normal şekilde çalıştırabilir. Yani esas işim altyapıyı değiştirmek değil, çok-şeritli motoru yazıp UTM YAML'ını tasarlamak.

Pratik plan kısaca şöyle olurdu:

1. `turinglab/multi_tape.py` içinde `MultiTapeTM` sınıfını yaz, YAML'da `num_tapes: 3` desteklensin.
2. Bir TM kodlama formatı seç. Bunun için iki yardımcı fonksiyon: `encode_machine(tm) -> str` ve `decode_machine(s) -> SingleTapeTM`.
3. UTM'i 3 şeritli olarak yaz: şerit 1 → kodlama, şerit 2 → simüle edilen durum, şerit 3 → simüle edilen bant.
4. Doğrulama için tek bir test: binary_increment'i hem doğrudan çalıştır, hem UTM aracılığıyla çalıştır, sonuçlar aynı olmalı.

Kavramsal olarak en hoş kısım şu: TuringLab şu anda Python'la yazılmış bir motor. UTM eklenince motor "kendi diline ait TM'leri çalıştırabilen" bir araç haline geliyor — küçük çaplı bir bootstrapping gibi. Performans çok kötü olur tabii (UTM, simüle ettiği makinenin her adımı için onlarca adım atar), ama amaç performans değil; hesaplama kuramının "evrensellik" sonucunu kendi gözünle somut kod olarak görmek.

## 5. Sınırlar ve İleri Çalışma

Şu anki halinde TuringLab'in birkaç açığı var. En temeli: yalnızca deterministik ve tek şeritli TM destekliyor. NTM ve multi-tape yok, yani bu motorla anlatabileceğim dillerin sınıfı sınırlı. Hesaplama gerçekten durduğunu bilemediği için `max_steps` parametresine bağımlı — bu zaten halting problemi gereği değiştirilemez ama yine de kullanıcıya daha iyi geri bildirim verebilirdim (mesela timeout olunca son durumdaki bant kesitini ekrana basmak).

Şerit görselleştirmesi `to_string` ile çalışıyor ama basit; daha uzun makinelerde okumak zorlaşıyor. Verbose mod sadece terminale basıyor, HTML/PNG çıktısı yok (Bonus D'yi yapsaydım çözülürdü).

Bir hafta daha olsaydı sırayla şunları yapardım:

1. **Çok şeritli motor + UTM** — yukarıdaki bölümdeki planı uygulardım. Bonus A'nın temelini bu hazırlardı.
2. **Görselleştirici** — Pillow ile her adımı PNG'ye çeviren basit bir `visualizer.py`. Bir GIF çıkarmak sunum kalitesini de ciddi artırırdı.
3. **CLI** — Şu an `python -c` ile import etmek zorundayım, `turinglab run machines/binary_increment.yaml 1011` gibi düzgün bir CLI yazardım.

Aslında üçü de motor değişikliği değil, motor üstüne araç eklemek — yani temel yapı bence olması gerektiği yerde duruyor.

## 6. Kaynakça

- Dr. Ali Çetinkaya, *TuringLab Öğrenci El Kitabı*, Selçuk Üniversitesi Bilgisayar Mühendisliği Bölümü, 2026 — ödev şartnamesi ve API beklentileri.
- Michael Sipser, *Introduction to the Theory of Computation*, 3rd ed., Cengage Learning, 2012 — Turing makineleri ve UTM bölümlerine başvurdum.
- PyYAML belgeleri — https://pyyaml.org/wiki/PyYAMLDocumentation (`safe_load` davranışı için).
- pytest belgeleri — https://docs.pytest.org/ (fixture ve `capsys` kullanımı için).
- Ders notları + Stack Overflow'da tek tek soru-cevap aramaları (hiçbirini olduğu gibi kopyalamadım).
